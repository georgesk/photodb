#!/usr/bin/python3

"""
A small web service based on cherrypy and opencv, which allow one
to normalize photos of faces
"""

import os, sys, cherrypy, sqlite3
from io import BytesIO

thisdir=os.path.dirname(__file__)
sys.path.insert(0, thisdir)
staticdir=os.path.join(thisdir,"static")
db=os.path.join(thisdir,'db','names.db')

def staticFile(path):
    """
    @return the content of a file in the static/ directory
    """
    return open(os.path.join(staticdir, path)).read()

import autoretouche, base64

class Retouche(object):
    
    @cherrypy.expose
    def index(self):
        return staticFile("portrait.html")
    
    @cherrypy.expose
    def test(self):
        return staticFile("test.html")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def chercheNom(self, term=None):
        """
        search the database in order to make an autocompletion
        on the First Name field
        """
        if term is None:
            return []
        result=[]
        c = sqlite3.connect(db).cursor()
        for row in c.execute("SELECT surname FROM person where surname like '%{}%'".format(term)):
            result.append(row[0])
        return result
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def cherchePrenom(self, **kw):
        """
        search the database in order to make an autocompletion
        on the Second Name field
        """
        if 'nom' not in kw or 'prenom' not in kw:
            return []
        result=[]
        c = sqlite3.connect(db).cursor()
        for row in c.execute("SELECT givenname FROM person WHERE surname = '{nom}' and givenname LIKE '{prenom}%'".format(**kw)):
            result.append(row[0])
        return result
        
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
