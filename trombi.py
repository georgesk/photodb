#!/usr/bin/python3

"""
Publications de paquets de 36 photos par page,
les photos sont prêtes à être imprimées avec un texte sous chacune
"""

from io import BytesIO, StringIO
import zipfile
import xml.dom.minidom
import os

def pageGen(template="templates/modele0.odt", data=[], title="Joli titre"):
    """
    Crée un fichier temporaire au format ODT
    @param template un fichier ODT comportant 36 places de tableau
    @param data une liste contenant au plus 36 photos et phrases
    @param title un titre pour la page
    @return un BytesIO contenant une page au format ODT
    """
    modele=zipfile.ZipFile(template)
    contents=modele.open("content.xml")
    zipIO=BytesIO()
    result=zipfile.ZipFile(zipIO,"x")
    for zinf in modele.infolist():
        f=zinf.filename
        if f!="content.xml":
            result.writestr(f,modele.read(zinf))
    page=xml.dom.minidom.parse(contents)
    print(page.toprettyxml(indent=" "))
    cells=page.getElementsByTagName("table:table-cell")
    title0=cells[0].getElementsByTagName("text:p")[0]
    title0.firstChild.replaceWholeText(title)
    i=1
    for photo, texte in data:
        # insertion de la photo
        image=cells[i].getElementsByTagName("draw:image")[0]
        target="Pictures/{}".format(os.path.basename(photo))
        image.setAttribute("xlink:href", target)
        with open(photo,"rb") as infile:
            result.writestr(target, infile.read())
        # insertion du texte
        t=cells[i].getElementsByTagName("text:s")[0].nextSibling
        t.replaceWholeText(texte)
        i+=1
        # limitation à 36 cases de tableau !
        if i > 36:
            break
        
    newcontents=StringIO()
    page.writexml(newcontents)
    newcontents.seek(0)
    result.writestr("content.xml", newcontents.read())
    result.close()
    zipIO.seek(0)
    return zipIO

if __name__=="__main__":
    import re
    pat=re.compile("_[0-9a-f]+\.jpg")
    def textFrom(f):
        return pat.sub("",f)
    
    example="/home/georgesk/tex/classes/2017-2018/photodb/var-lib-photodb/photodb/photos"
    _,_,fnames=next(os.walk(example))
    fnames=[f for f in fnames if f.endswith('.jpg')]
    data=[(os.path.join(example,f),textFrom(f)) for f in fnames[:36]]
    zipIO=pageGen(data=data)
    with open("/tmp/montest.odt",'wb') as outfile:
        outfile.write(zipIO.read())
