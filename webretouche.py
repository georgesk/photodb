#!/usr/bin/python3

"""
A small web service based on cherrypy and opencv, which allow one
to normalize photos of faces
"""

import os, sys, cherrypy, sqlite3, re, uuid, base64
from io import BytesIO

thisdir=os.path.dirname(__file__)
sys.path.insert(0, thisdir)
staticdir=os.path.join(thisdir,"static")
db=os.path.join(thisdir,'db','names.db')
jpgPrefix=b'data:image/jpeg;base64,'

from autoretouche import jpgPrefix, FaceImage


def protect(s):
    """
    prepare a name to be compatible with every file system
    @ a string with no spaces, no diacritics, etc.
    """
    return re.sub(r'[^A-Za-z0-9_\-]','_',s)

def nommage(nom, prenom):
    """
    return a unique file name based on two strings
    @param nom surname
    @param prenom given name
    @return a unique filename
    """
    result=protect(nom)+'_'+protect(prenom)
    result=result[:20]+'_'+str(uuid.uuid1())+'.jpg'
    return result
    

def staticFile(path):
    """
    @return the content of a file in the static/ directory
    """
    return open(os.path.join(staticdir, path)).read()

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
    def envoi(self, **kw):
        """
        callback page to deal with first and second name, plus an image
        """
        keys=('nom','prenom','photo')
        for k in keys:
            if k not in kw:
                return {"statut": "ko"}
        fi = FaceImage(kw['photo'].encode("utf-8"))
        if not fi.ok: # first check whether a face has been detected
            return {
                "statut": "malretouche", # bad face recognition
            }
        conn=sqlite3.connect(db)
        c = conn.cursor()
        rows=list(c.execute("SELECT photo FROM person where surname = '{nom}' and givenname = '{prenom}'".format(**kw)))
        if not rows:
            return {"statut": "nouveau"}
        row=rows[0]
        if row[0]: # there is a photo
            path=os.path.join(thisdir, 'photos',row[0])
            try:
                b64=jpgPrefix+base64.b64encode(open(path,'rb').read())
            except:
                b64=jpgPrefix+base64.b64encode(open(os.path.join(thisdir,"nobody.jpg"),'rb').read())
            return {"statut": "dejavu","base64": b64,}
        else: # there is no photo so far
            fichier=nommage(kw['nom'],kw['prenom'])
            fi.saveAs(os.path.join(thisdir,'photos',fichier))
            c.execute("UPDATE person SET photo='{fichier}' WHERE surname = '{nom}' and givenname = '{prenom}'".format(fichier=fichier,**kw))
            conn.commit()
            return {
                "statut": "ok",
                "fichier": fichier,
                "base64": fi.toDataUrl,
            }
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def force_envoi(self, **kw):
        """
        callback page to deal with first and second name, plus an image
        when the image must be overwritten
        """
        keys=('nom','prenom','photo')
        for k in keys:
            if k not in kw:
                return {"statut": "ko"}
        fi = FaceImage(kw['photo'].encode("utf-8"))
        if not fi.ok: # first check whether a face has been detected
            return {
                "statut": "malretouche", # bad face recognition
            }
        conn=sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT photo FROM person where surname = '{nom}' and givenname = '{prenom}'".format(**kw))
        for row in c: # erase the previous photo
            try:
                os.unlink(os.path.join(thisdir,"photos",row[0]))
            except:
                pass
        fichier=nommage(kw['nom'],kw['prenom'])
        fi.saveAs(os.path.join(thisdir,'photos',fichier))
        c.execute("UPDATE person SET photo='{fichier}' WHERE surname = '{nom}' and givenname = '{prenom}'".format(fichier=fichier,**kw))
        conn.commit()
        return {
            "statut": "ok",
            "fichier": fichier,
            "base64": fi.toDataUrl,
        }
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def retouche(self, data=None):
        """
        @param data should be an url-encoded JPG image
        (magic bytes: 'data:image/jpeg;base64,')
        @return a JSON response, with status => "OK" when a face was recognized
        then imgdata => an url-encoded JPG image. If the status is something
        else, an anonymous image is loaded in imgdata.
        """
        if data is None:
            with open("nobody.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            data=jpgPrefix+encoded_string
        else:
            data=data.encode("utf-8") # to bytes
        fi = FaceImage(data)
        status = "OK" if fi.ok else "Face auto-detection failed"
        return {
            "status": status,
            "imgdata": fi.toDataUrl,
        }

if __name__=="__main__":
    cherrypy.quickstart(Retouche(),'/','cherryApp.conf')
