import rhinoscriptsyntax as rs
import Rhino as rh

def divideCurve(crv):
    aRating = rs.GetInteger("What level of accuracy do you want? (1-10)", 1, 1, 10)
    divPoints = aRating/5 * 200
    divPoints = int(divPoints)
    points = rs.DivideCurve(crv, divPoints, create_points = False, return_points = True)
    return points

def plotPoint(pOne, pTwo):
    line = rs.AddLine(pOne, pTwo)
    coordinates = rs.CurveMidPoint(line)
    point = rs.AddPoint(coordinates)
    rs.DeleteObject(line)
    translation = rs.Distance(pOne, pTwo)
    rs.MoveObject(point, (0,0,translation))
    result = rs.PointCoordinates(point)
    rs.DeleteObject(point)
    return result

def operation(list, mList):
    step = 0
    max = len(list)
    while (step < max):
        sList = []
        sStep = 1
        sMax = len(list)
        while (sStep < sMax):
            addPoint = plotPoint(list[0], list[sStep])
            sList.append(addPoint)
            sStep = sStep + 1
        list.pop(0)
        mList.append(sList)
        step = step + 1

def pointsToSurface(listOne, listTwo, sList):
    listOneCopy = list(listOne)
    listTwoCopy = list(listTwo)
    while True:
        if (len(listOneCopy) < 2 or len(listTwoCopy) < 2):
            break
        else:
            line = rs.AddLine(listOneCopy[0], listOneCopy[1])
            sOne = rs.ExtrudeCurvePoint(line, listTwoCopy[0])
            rs.DeleteObject(line)
            line = rs.AddLine(listTwoCopy[0], listTwoCopy[1])
            sTwo = rs.ExtrudeCurvePoint(line, listOneCopy[1])
            rs.DeleteObject(line)
            listOneCopy.pop(0)
            listTwoCopy.pop(0)
            sList.append(sOne)
            sList.append(sTwo)

def listShuffle(listOne):
    nList = list(listOne)
    step = 0
    max = len(nList)
    while (step <= max):
        nList.append(nList.pop(0))
        step += 1 
    return nList

inputPoints = []
rInputPoints = []
sInputPoints = []
masterList = []
rMasterList = []
sMasterList = []
resultingSurfaces = []
rResultingSurfaces = []
sResultingSurfaces = []
sublist = []

inputCrv = rs.GetObject("Select the input curve.", 4)
rs.EnableRedraw(False)
inputPoints = divideCurve(inputCrv)
rInputPoints = listShuffle(inputPoints)
sInputPoints = listShuffle(rInputPoints)
rs.HideObject(inputCrv)
operation(inputPoints, masterList)
operation(rInputPoints, rMasterList)
operation(sInputPoints, sMasterList)

for i in range(len(masterList)):
    x = i + 1
    if x >= len(masterList):
        print "Done One"
        break
    else:
        pointsToSurface(masterList[i], masterList[x], resultingSurfaces)

for i in range(len(rMasterList)):
    x = i + 1
    if x >= len(rMasterList):
        print "Done Two"
        break
    else:
        pointsToSurface(rMasterList[i], rMasterList[x], rResultingSurfaces)

for i in range(len(sMasterList)):
    x = i + 1
    if x >= len(sMasterList):
        print "Done Three"
        break
    else:
        pointsToSurface(sMasterList[i], sMasterList[x], sResultingSurfaces)

rSurfaces = resultingSurfaces + rResultingSurfaces + sResultingSurfaces

rs.SelectObjects(rSurfaces)
rs.Command("_Mesh")
rs.Command("_Delete")
rs.Command("_SelDup")
rs.Command("_Delete")

rs.EnableRedraw(True)
rMeshes = rs.GetObjects("Select resulting meshes", 32)

finalMesh = rs.JoinMeshes(rMeshes, True )
