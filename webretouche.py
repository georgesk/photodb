#!/usr/bin/python3

"""
A small web service based on cherrypy and opencv, which allow one
to normalize photos of faces
"""

import os, sys, cherrypy, sqlite3, re, uuid, base64
from io import BytesIO
from datetime import datetime

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

def timestamp():
    """
    @return a UTC time stamp
    """
    return datetime.utcnow().isoformat(sep=" ", timespec="seconds")

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
        @param kw dictionary of named parameters, with mandatory keys:
        nom, prenom, photo
        @return dictionary with those keys: status and message; when
        status is not "ko", two other keys are given: fname and base64
        """
        keys=('nom','prenom','photo')
        # give an error message when one parameter is missing or empty
        missingKeys=[k for k in keys if k not in kw]
        missingVals=[k for k in kw if not kw[k]]
        if missingKeys + missingVals:
            return {
                "status": "ko",
                "message": "appel erroné, paramètres incorrects: {l}".format(l=",".join(missingKeys + missingVals)),
            }
        fi = FaceImage(kw['photo'].encode("utf-8"))
        #### default return components, when no face is detected ####
        status="malretouche"
        fname=""
        base64=fi.toDataUrl
        message="""<p>Le système détecte mal le visage à recadrer.</p>
<p>Veuillez refaire la photo.</p>
"""
        if fi.ok:
            # a face was detected, good!
            fname=nommage(kw['nom'],kw['prenom'])
            fi.saveAs(os.path.join(thisdir,'photos',fname))
            conn=sqlite3.connect(db)
            c = conn.cursor()
            rows=list(c.execute("""
SELECT photo FROM person
WHERE surname = '{nom}' and givenname = '{prenom}'
""".format(**kw)))
            if not rows:
                # the user does not exist so far: create a new entry
                status="nouveau"
                message="""
<p>Nouvel enregistrement créé pour {nom} {prenom}</p>
""".format(**kw)
                c.execute("""
INSERT INTO person (surname, givenname, photo, date) 
VALUES ('{nom}','{prenom}','{fname}','{date}')
""".format(fname=fname,date=timestamp(),**kw))
                conn.commit()
            else:
                photo=rows[0][0]
                # the user already exists, make an update
                status="ok"
                message="""
<p>Enregistrement de la photo effectué pour {nom} {prenom}</p>
""".format(**kw)
                if photo: # erase an earlier photo file
                    moremessage="<p>L'ancienne photo n'existait pas : erreur ?</p>"
                    try:
                        os.unlink(os.path.join(thisdir,'photos',photo))
                        moremessage="<p>L'ancienne photo a été effacée</p>"
                    except:
                        pass
                    message+=moremessage
                # the update is made in either case, even if there was no photo
                c.execute("""
UPDATE person SET photo='{fname}', date='{date}'
WHERE surname = '{nom}' and givenname = '{prenom}'
""".format(fname=fname,date=timestamp(),**kw))
                conn.commit()
        # in any case, return status, fname, base64 message
        return {
            "statut": "ok",
            "fname": fname,
            "base64": fi.toDataUrl,
            "message": message,
        }
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def encadre(self, **kw):
        """
        callback page to get the rectangle of a recognized face, if any
        @param kw the keywords with keys "photo", "nom", "prenom"
        which yields a dataURL encoded JPG image
        """
        fi = FaceImage(kw['photo'].encode("utf-8"))
        c = sqlite3.connect(db).cursor()
        rows=list(c.execute("SELECT photo FROM person where surname = '{nom}' and givenname = '{prenom}'".format(**kw)))
        message=""
        oldimage=""
        if not rows:
            message="Inconnu(e) dans la base"
            cssclass="red"
        else:
            message="Trouvé(e) dans la base"
            cssclass="green"
            photo=rows[0][0]
            if photo:
                photo=open(os.path.join(thisdir,"photos",photo),'rb').read()
                photo=jpgPrefix+base64.b64encode(photo)
                oldimage=photo.decode("ascii")
                message="Trouvé(e) avec la photo"
                cssclass="orange"
        return {
            "status": fi.ok,
            "rect": fi.cropRect,
            "message": message,
            "oldimage": oldimage,
            "cssclass": cssclass,
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
    print("service dans quelques secondes à http://localhost:8901")
    cherrypy.quickstart(Retouche(),'/','cherryApp.conf')
