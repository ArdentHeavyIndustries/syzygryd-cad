#
# A Python script for preparing cubes.
# Please note that I don't actually know Python.
#
# Ian Baker <ian@sonic.net>
# GPL'd.

import rhinoscriptsyntax as rs
from System.Drawing import Color
import re

def labelObject(color):

    # R C
    # Y G
    # O B
    
    # fetch an object.
    curves = rs.GetObjects("Select objects for " + color, rs.filter.curve)
    if( curves == None):
        return

    if( len(curves) > 1 ):
        rs.UnselectObjects(curves)
        labelCurve = rs.JoinCurves(curves, delete_input=True)
        if(len(labelCurve) > 1):
            print "Created more than one object for " + color
            return

        if(not rs.IsCurveClosed(labelCurve[0])):
            print "Created an open curve for " + color + ". Fix it and try again."
            return

        # now, we're working with just one curve.
        curves = labelCurve

    rs.ObjectLayer(curves[0], "CUT")

    docName = rs.DocumentName()
    
    p = re.compile('cube_(\d+)')
    m = p.search(rs.DocumentName())
    if(not m):
        cubeNumber = 0
    else:
        cubeNumber = m.groups()[0]
    
    text = rs.AddText(str(int(cubeNumber)) + color, rs.CurveAreaCentroid(curves[0])[0], 1.0, "Helvetica")

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
    layerSetup()
    # Call the function defined above
    labelObject("R")
    labelObject("C")
    labelObject("Y")
    labelObject("G")
    labelObject("O")
    labelObject("B")

    deleteRemainingStuff()
