#!/usr/bin/python3

"""
A small web service based on cherrypy and opencv, which allow one
to normalize photos of faces
"""

import os, sys, cherrypy
from io import BytesIO

thisdir=os.path.dirname(__file__)
sys.path.insert(0, thisdir)

import autoretouche, base64

class Retouche(object):
    
    @cherrypy.expose
    def index(self):
        return open("test.html").read()
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def retouche(self, data=None):
        jpgPrefix=b'data:image/jpeg;base64,'
        if data is None:
            with open("nobody.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            data=jpgPrefix+encoded_string
        else:
            data=data.encode("utf-8") # to bytes
        imgdata=BytesIO()
        result= autoretouche.cropImage(BytesIO(data),imgdata)
        status = "OK" if result else "Face auto-detection failed"
        return {
            "status": status,
            "imgdata": imgdata.getvalue(),
        }

    @cherrypy.expose
    def retoucheHTML(self, data=None):
        jpgPrefix=b'data:image/jpeg;base64,'
        if data is None:
            with open("nobody.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            data=jpgPrefix+encoded_string
        else:
            data=data.encode("utf-8") # to bytes
        imgdata=BytesIO()
        result= autoretouche.cropImage(BytesIO(data),imgdata)
        status = "OK" if result else "Face auto-detection failed"
        return """<html>
<head></head>
<body>
  <h1>{status}</h1>
  <img src="{imgdata}"/>
</body>
</html>
""".format(
    status=status,
    imgdata=imgdata.getvalue().decode("utf-8")
)

if __name__=="__main__":
    cherrypy.quickstart(Retouche(),'/','cherryApp.conf')