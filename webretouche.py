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
        return "Hello World! Here is the face normalizing service"
    
    @cherrypy.expose
    def test(self):
        return open("static/test.html").read()
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def retouche(self, data=None):
        """
        The web page /retouche can recieve data either by GET or POST
        @param data should be an url-encoded JPG image
        (magic bytes: 'data:image/jpeg;base64,')
        @return a JSON response, with status => "OK" when a face was recognized
        then imgdata => an url-encoded JPG image. If the status is something
        else, an anonymous image is loaded in imgdata.
        """
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

if __name__=="__main__":
    cherrypy.quickstart(Retouche(),'/','cherryApp.conf')
