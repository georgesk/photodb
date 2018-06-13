#!/usr/bin/python3

"""
Reconnaissance faciale, recadrage et harmonisation des photos du trombinoscope
Jean-Bart

Dépendances logicielles:
python3-opencv
"""

import cv2, sys, math, os, os.path
import numpy as np
from PIL import Image
from io import BytesIO
import base64

__thisdir=os.path.dirname(__file__)
__cascPath = os.path.join(__thisdir,"haarcascade_frontalface_default.xml")
__CASCADE = cv2.CascadeClassifier(__cascPath)

def cropImage(indata, outdata,size=(150,192)):
    """
    Cherche un visage dans l'image de nom de fichier fname, située dans le
    répertoire indir; découpe l'image et la place dans le répertoire outdir
    si c'est possible. Émet un message de réussite ou d'erreur
    @param indata un fichier de bytes ouvert avec l'image source
    @param outdata un fichier de bytes ouvert pour l'image retouchée
    @param size la dimension de l'image retouchée (largeur, hauteur)
    @return True quand un visage a été traité
    """
    jpgPrefix=b'data:image/jpeg;base64,'
    val=indata.getvalue()
    if val[:len(jpgPrefix)]==jpgPrefix:
        val=val[len(jpgPrefix):]
    image=np.array(Image.open(BytesIO(base64.b64decode(val))))
    image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = __CASCADE.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    if len(faces)==0 or len(faces)>1:
        result=False
        resized_image=image
    else:
        result=True
        x, y, w, h = faces[0]
        # calcul du paramètre a tel que 25a * 32a ait la même surface que 2 * w * h
        a=math.sqrt(2*w*h/800)
        #coordonnées du coin haut gauche
        x1=round(x+w/2-12.5*a); y1=round(y+7/12*h-16*a)
        x1=int(max(x1,0)); y1=int(max(y1,0))
        #coordonnées du coin bas droite
        x2=round(x+w/2+12.5*a);y2=round(y+7/12*h+16*a)
        x2=int(min(x2,width)); y2=int(min(y2,height))
        crop_img=image[y1:y2, x1:x2]
        hsv=cv2.cvtColor(crop_img,cv2.COLOR_RGB2HSV)
        h,s,v = cv2.split(hsv)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
        h1=h
        #s1 = clahe.apply(s)
        s1=s
        v1 = clahe.apply(v)
        hsv1=cv2.merge((h1,s1,v1))
        newimg=cv2.cvtColor(hsv1, cv2.COLOR_HSV2RGB)
        resized_image = cv2.resize(newimg, size) 
    data=cv2.imencode(".jpg",resized_image)[1].tostring()
    data=jpgPrefix+base64.b64encode(data)
    outdata.write(data)
    return result

if __name__=="__main__":
    with open(sys.argv[1],"rb") as infile:
        with open(sys.argv[2],"wb") as outfile:
            cropImage(infile=infile, outfile=outfile)
