#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Reconnaissance faciale, recadrage et harmonisation des photos du trombinoscope
Jean-Bart

Dépendances logicielles:
python-opencv
"""

from __future__ import print_function, division

import cv2, sys, math, os, os.path

def cropImage(fname, cascade,
              indir="photos", outdir="photos_recadrees",
              output=sys.stderr, size=(150,192)):
    """
    Cherche un visage dans l'image de nom de fichier fname, située dans le
    répertoire indir; découpe l'image et la place dans le répertoire outdir
    si c'est possible. Émet un message de réussite ou d'erreur
    @param fname nom d'un fichier photo
    @param indir chemin du répertoire d'origine
    @param outdir chemin du répertoire de destination
    @param output flux de sortie des messages
    @param size la dimension (largeur x hauteur)
    """
    image = cv2.imread(os.path.join(indir, fname))
    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags = cv2.cv.CV_HAAR_SCALE_IMAGE
    )

    if len(faces)==0 or len(faces)>1:
        output.write("ERREUR : visage mal reconnu dans {}\n".format(fname))
        cv2.imwrite(os.path.join(outdir,"erreurs",fname),image)
    else:
        output.write("OK : {}\n".format(fname))
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
        img2=cv2.cvtColor(crop_img, cv2.COLOR_RGB2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
        cl1 = clahe.apply(img2)
        resized_image = cv2.resize(cl1, size) 
        newFname=os.path.join(outdir, fname)
        cv2.imwrite(newFname,resized_image)
    return

if __name__=="__main__":
    cascPath = "haarcascade_frontalface_default.xml"
    indir="photos"
    outdir="photos_retouchees"
    try:
        os.makedirs(outdir+"/erreurs")
    except:
        pass
    for fname in sorted(list(os.listdir(indir))):
        if fname.endswith(".jpg"):
            cropImage(fname, cv2.CascadeClassifier(cascPath),
                      indir=indir, outdir=outdir)
