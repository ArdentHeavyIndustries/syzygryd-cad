#
# A Python script for preparing acrylic cubes
# Please note that I don't actually know Python.
#
# Ian Baker <ian@sonic.net>
# GPL'd.

import rhinoscriptsyntax as rs
from System.Drawing import Color
import re

def obtainScaleFactor():
    # obtain kerf
    kerf=rs.GetReal("Cut kerf width", .006)

    # obtain two points
    point1 = rs.GetPoint("Base dimension start point")
    point2 = rs.GetPoint("Base dimension end point")

    if(point1 == None or point2 == None):
        return

    distance = rs.Distance(point1, point2)
    if(distance == 0):
        return

    factor = 1 + kerf/distance

    return factor

def labelScaleObject(color, factor):

    # R C
    # Y G
    # O B

    # which cube are we working with?
    docName = rs.DocumentName()

    if(docName):
        p = re.compile('cube_(\d+)')
        m = p.search(rs.DocumentName())
        if(not m):
            cubeNumber = 0
        else:
            cubeNumber = m.groups()[0]
    else:
        cubeNumber = 0
   
    sideName = str(int(cubeNumber)) + color

    # fetch the curves that make up the cube faces
    curves = rs.GetObjects("Select objects for " + color, rs.filter.curve)
    if( curves == None):
        return

    if( len(curves) > 1 ):
        rs.UnselectObjects(curves)
        labelCurves = rs.JoinCurves(curves, delete_input=True)
        if(len(labelCurves) > 2):
            print "Created more than two objects for " + color
            return

        if( not rs.IsCurveClosed(labelCurves[0]) or not rs.IsCurveClosed(labelCurves[1]) ):
            print "Created an open curve for " + color + ". Fix it and try again."
            return
        curves = labelCurves

    origin = rs.GetPoint("Scale origin point for " + color)

    # curves is now the joined edges, instead of the individual lines
    if(len(curves) > 1):
        # group the curves if there's still more than one.
        faceGroup = rs.AddGroup(sideName)
        rs.AddObjectsToGroup(curves, sideName)

        rs.ObjectLayer(faceGroup, "CUT")
    else:
        rs.ObjectLayer(curves[0], "CUT")

    rs.ScaleObjects(curves, origin, (factor, factor, 1))


    text = rs.AddText(sideName, rs.CurveAreaCentroid(curves[0])[0], 1.0, "Helvetica")

    # this crap is all here for making the text centered instead of left-justified
    box = rs.BoundingBox(text)
    textPoint = rs.TextObjectPoint(text)
    rs.TextObjectPoint(text, [textPoint[0] - (box[1][0] - box[0][0])/2, textPoint[1] - (box[3][1] - box[0][1])/2, textPoint[2]])

    rs.ObjectLayer(text, "DISPLAY")

    
def layerSetup():
    # create layers we need, set colors.
    if(not rs.IsLayer("CUT")):
        rs.AddLayer("CUT", Color.Red)
    
    if(not rs.IsLayer("DISPLAY")):
        rs.AddLayer("DISPLAY", Color.FromArgb(100, 149, 237))  #cornflower blue

    rs.CurrentLayer("CUT")

def deleteRemainingStuff():
    # get all the objects that aren't on a special layer
    objects = rs.AllObjects()
    for object in objects:
        objLayer = rs.ObjectLayer(object)
        if(not (objLayer == "CUT" or objLayer == "DISPLAY")):
            rs.DeleteObject(object)
    

    # delete all layers that aren't useful here.
    layers = rs.LayerNames()
    if(layers != None):
        for layer in layers:
            if(layer != "CUT" and layer != "DISPLAY"):
                rs.DeleteLayer(layer)


if( __name__ == '__main__' ):
    factor = obtainScaleFactor()
    layerSetup()

    # Call the function defined above
    labelScaleObject("R", factor)
    labelScaleObject("C", factor)
    labelScaleObject("Y", factor)
    labelScaleObject("G", factor)
    labelScaleObject("O", factor)
    labelScaleObject("B", factor)

#    deleteRemainingStuff()
