import rhinoscriptsyntax as rs
import sys
from random import *
import copy
import time
import Rhino

"""A script with the purpose of organizing a large set of closed curves -- building footprints -- by area. The interntion is to be able to rapidly create graphics of the ordered building footprints
for multiple cities giving the viewer the ability to analyze the typologies that exist there."""

#Collect the footprints to be sorted and define "orderedCurves" as a library and "sortedCurves" as the resulting list of ordered footprints.
inputCurves = rs.GetObjects("Select the building footprints to be organized.", filter=4,preselect=True, minimum_count=0)

def getArea(input):
	return rs.Area(input)

sortedCurves = sorted(inputCurves, key=getArea)

rs.EnableRedraw(False)


#Begin linear ordering. First placement is the exception, then the other ones are placed based upon that.
def findAnchorPoint(crv):
    #AnchorPoint is the bottom left point of the building's boundingbox. This is the vector start from which the footprint is moved to align to the AnchorPoint of the previous footprint. Returns the point.
    boundingBox = rs.BoundingBox(crv, in_world_coords=True)
    return boundingBox[0]

def findHOffset(prevCrv, currentCrv):
    #The offset is equal to the width of the previous footprint's bounding box plus 1/8 of the width of the current footprint's bounding box. Returns the x-transformation amount.
    prevBox = rs.BoundingBox(prevCrv, in_world_coords=True)
    currentBox = rs.BoundingBox(currentCrv, in_world_coords=True)
    prevSpacing = rs.Distance(prevBox[0], prevBox[1])
    currentSpacing = rs.Distance(currentBox[0], currentBox[1])
    currentSpacing = currentSpacing * 0.25
    offset = prevSpacing + currentSpacing
    return offset

rs.MoveObject(sortedCurves[0], rs.VectorCreate((0,0,0), findAnchorPoint(sortedCurves[0]))) #Place the first footprint.

for i in range(len(sortedCurves)): #Place the other footprints.
    if i == len(sortedCurves) - 1:
        break
    else:
        rs.MoveObject(sortedCurves[i+1], rs.VectorCreate(findAnchorPoint(sortedCurves[i]),findAnchorPoint(sortedCurves[i+1])))
        rs.MoveObject(sortedCurves[i+1], (findHOffset(sortedCurves[i], sortedCurves[i+1]),0,0))

#Begin vertical ordering. The process consists of first finding the total length of all the footprints, adding the height of the total boundingbox, then finding the square root of the result.
totalBox = rs.BoundingBox(sortedCurves)
sqrtSource = rs.Distance(totalBox[0], totalBox[1])
minLength = sqrtSource**0.5


def devLenFactor(oList):
    def getX(point):
        pCood = rs.PointCoordinates(point)
        return pCood[0]
    
    def findFactor(startEnd):
        factor = uniform(startEnd[0], startEnd[1])
        return factor
    
    def findFitness(point):
        def testArrangement(sortedCurves, factor):
            totalBox = rs.BoundingBox(sortedCurves)
            sqrtSource = rs.Distance(totalBox[0], totalBox[1])
            minLength = sqrtSource**0.5
            
            minLength = minLength ** factor
            
            def meetsLength(len, startCrv, endCrv):
                objects = [startCrv, endCrv]
                boundingBox = rs.BoundingBox(objects, in_world_coords=True)
                curLen = rs.Distance(boundingBox[0], boundingBox[1])
                if curLen >= len:
                    return True
                else:
                    return False
            
            #Then, defining a list of the resulting lists.
            listOfLists = []
            s = 0 #"Start"
            e = 0 #"End"
            
            #Loop that splits the list into smaller lists.
            while True:
                if (s + e) == len(sortedCurves) or s == len(sortedCurves):
                    listOfLists.append(sortedCurves[s:s+e])
                    break
                elif meetsLength(minLength, sortedCurves[s], sortedCurves[s+e]) == True:
                    listOfLists.append(sortedCurves[s:s+e])
                    s = s + e
                    e = 1
                    continue
                else:
                    e += 1
                    continue
            
            #Now to move them vertically. First, like with the horizontal movement, we need to create a function that finds the vertical offset between each line.
            def findVOffset(curCrv):
                currentBox = rs.BoundingBox(curCrv, in_world_coords=True)
                vHeight = rs.Distance(currentBox[0], currentBox[3])
                offset = vHeight * 1.125
                offset = 0 - offset
                return offset
            
            #And to move them.
            for i in range(len(listOfLists)):
                if i == len(listOfLists) - 1:
                    break
                else:
                    rs.MoveObject(listOfLists[i+1], rs.VectorCreate(findAnchorPoint(listOfLists[i]),findAnchorPoint(listOfLists[i+1])))
                    rs.MoveObject(listOfLists[i+1], (0,findVOffset(listOfLists[i+1]),0))
        
        sList = rs.CopyObjects(oList)
        rs.ShowObjects(sList)
        testArrangement(sList, point[0])
        
        shapeBox = rs.BoundingBox(sList)
        width = rs.Distance(shapeBox[0], shapeBox[1])
        height = rs.Distance(shapeBox[0], shapeBox[3])
        
        numerator = abs(width - height)
        denominator = width + height
        denominator = denominator / 2
        fitness = numerator / denominator
        fitness = fitness * 100
        rs.DeleteObjects(sList)
        return fitness
    
    def returnFit(point):
        return point[1]
    
    def findAverageFactor(list):
        total = 0
        for a in list:
            total += a[0]
        total = total / len(list)
        return total
    
    def findAverageFitness(list):
        total = 0
        for a in list:
            total += a[1]
        total = total / len(list)
        return total
    
    def findRange(pOne, pTwo):
        start = pOne[0]
        end = pTwo[0]
        
        range = end - start
        range = abs(range)
        return range
    
    startEnd =[0.5, 2]
    genCount = 0
    count = 1
    finish = 0
    fFactor = 0
    totalAttempts = 0
    
    count = rs.GetInteger("How many GENERATIONS would you like to start with?", 1, 1, 10)
    
    while True:
        startTime = time.time()
        while count > 0:
            species = []
            genCount += 1
            step = 0
            while step <= 50:
                totalAttempts += 1
                point = [0, 0]
                point[0] = findFactor(startEnd)
                point[1] = findFitness(point)
                species.append(point)
                step += 1
            sSpecies = sorted(species, key=returnFit)
            
            topAverage = findAverageFactor(sSpecies[0:9])
            topRange = findRange(sSpecies[0], sSpecies[9])
            
            startEnd[0] = topAverage - (1.5*abs(topRange))
            startEnd[1] = topAverage + (1.5*abs(topRange))
            
            count -= 1
        
        bestPoint = sSpecies[0]
        totalAverageFactor = findAverageFactor(sSpecies)
        totalAverageFitness = findAverageFitness(sSpecies)
        
        endTime = time.time()
        duration = endTime - startTime
        duration = int(duration)
        rs.EnableRedraw(True)
        print " "
        print "GENERATIONS completed in [", duration, "] SECONDS."
        print " "
        print "After [" , genCount, "] GENERATIONS, the average FACTOR is [", totalAverageFactor, "] and the average FITNESS is [", totalAverageFitness,"]."
        print "The best iteration had a FACTOR of [", bestPoint[0], "] and a FITNESS of [", bestPoint[1], "]."
        print " "
        query = rs.GetString("Would you like to CONTINUE iterating, or END iterating and accept the current best?", "CONTINUE", ["CONTINUE", "END"])
        if query == "END":
            break
        else:
            print " "
            count = rs.GetInteger("How many GENERATIONS would you like to iterate?", 1, 1, 100)
            print " "
            print "CONTINUING iterating for [", count, "] GENERATIONS."
            rs.EnableRedraw(False)
            continue
    print " "
    print "The iterations have ENDED. [", totalAttempts, "] solutions were tested."
    print "Your final best fit had a FACTOR of [", bestPoint[0], "] and a FITNESS of [", bestPoint[1], "]."
    fFactor = bestPoint[0]
    return fFactor

rs.HideObjects(sortedCurves)
minLenFactor = devLenFactor(sortedCurves)
rs.ShowObjects(sortedCurves)
minLength = minLength ** minLenFactor


#Now, split the list into smaller lists, first with defining a function that tests whether the length meets the criteria. Returns either True or False.
def meetsLength(len, startCrv, endCrv):
    objects = [startCrv, endCrv]
    boundingBox = rs.BoundingBox(objects, in_world_coords=True)
    curLen = rs.Distance(boundingBox[0], boundingBox[1])
    if curLen >= len:
        return True
    else:
        return False

#Then, defining a list of the resulting lists.
listOfLists = []
s = 0 #"Start"
e = 0 #"End"

#Loop that splits the list into smaller lists.
while True:
    if (s + e) == len(sortedCurves) or s == len(sortedCurves):
        listOfLists.append(sortedCurves[s:s+e])
        break
    elif meetsLength(minLength, sortedCurves[s], sortedCurves[s+e]) == True:
        listOfLists.append(sortedCurves[s:s+e])
        s = s + e
        e = 1
        continue
    else:
        e += 1
        continue

#Now to move them vertically. First, like with the horizontal movement, we need to create a function that finds the vertical offset between each line.
def findVOffset(curCrv):
    currentBox = rs.BoundingBox(curCrv, in_world_coords=True)
    vHeight = rs.Distance(currentBox[0], currentBox[3])
    offset = vHeight * 1.125
    offset = 0 - offset
    return offset

#And to move them.
for i in range(len(listOfLists)):
    if i == len(listOfLists) - 1:
        break
    else:
        rs.MoveObject(listOfLists[i+1], rs.VectorCreate(findAnchorPoint(listOfLists[i]),findAnchorPoint(listOfLists[i+1])))
        rs.MoveObject(listOfLists[i+1], (0,findVOffset(listOfLists[i+1]),0))


#Now to create the square bounding box for it.
initialBox = rs.BoundingBox(sortedCurves)
iBoxX = rs.Distance(initialBox[0], initialBox[1])
iBoxY = rs.Distance(initialBox[0], initialBox[3])
if iBoxX >= iBoxY:
    boxDim = iBoxX
else:
    boxDim = iBoxY
initialBorder = rs.AddRectangle(rs.WorldXYPlane(), boxDim, boxDim)
iBBox = rs.BoundingBox(initialBorder)
rs.MoveObject(initialBorder, rs.VectorCreate(initialBox[3], iBBox[3]))
centroid = rs.CurveAreaCentroid(initialBorder)
initialBorder = rs.ScaleObject(initialBorder, centroid[0], [1.125, 1.125, 1.125], False)


#Align all the rows horizontally
tCenterLine = boxDim / 2
for group in listOfLists:
    gBox = rs.BoundingBox(group)
    gBoxDim = rs.Distance(gBox[0], gBox[1])
    iCenterLine = gBoxDim / 2
    htranslation = tCenterLine - iCenterLine
    rs.MoveObject(group, (htranslation, 0, 0))


#Align total group vertically
tCenterLine = boxDim / 2

gBox = rs.BoundingBox(sortedCurves)
gBoxDim = rs.Distance(gBox[0], gBox[3])
iCenterLine = gBoxDim / 2
vtranslation = tCenterLine - iCenterLine
rs.MoveObject(sortedCurves, (0, -vtranslation, 0))


#Offset the border to give a margin.
"""
    Steps Left:
    5. Offset Border to create Margin (Variable?)
    6. How to make
    
    Issues Seen:
    More rectangular than desired.
        Smart offset to make more square
        Area under triangle of average height divided by the sqrt(TOTAL LENGTH)
    Variable Margin
    Add Paper Dimensions
        3x4 -- 3x3 is for the figure ground, 3x1 is for the title
    Option to Distribute the Bottom row Horizontally
 
    
"""