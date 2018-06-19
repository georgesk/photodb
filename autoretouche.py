#!/usr/bin/python3

"""
Reconnaissance faciale, recadrage et harmonisation des photos du trombinoscope
Jean-Bart

Dépendances logicielles:
python3-opencv, python3-numpy
"""

import cv2, sys, math, os, os.path
import numpy as np
from PIL import Image
from io import BytesIO
import base64

thisdir=os.path.dirname(__file__)
jpgPrefix=b'data:image/jpeg;base64,'

class FaceImage(object):
    """
    a class to implement an image with face detection
    """
    __CASCADE = cv2.CascadeClassifier(os.path.join(
        thisdir,"haarcascade_frontalface_default.xml"))
        
    def __init__(self, indata, size=(150,192)):
        """
        the constructor
        @param indata either a file name for an image or a bytes with
        an URL-encoded image
        @param size the size (width, height) of the cropped face to get
        """
        self.photo=None # should become a cv2 image
        self.size=size
        self.cropRect={}   # should become ("x":x, "y":y, "w":w, "h":h)
        self.cropped=None  # should become a cv2 image
        self.ok=False      # will become True when a face is detected
        if type(indata) == str and os.path.exists(indata):
            self.photo=cv2.imread(indata)
        elif type(indata) == bytes and indata[:len(jpgPrefix)] == jpgPrefix:
            photo=BytesIO(base64.b64decode(indata[len(jpgPrefix):]))
            photo=np.array(Image.open(photo))
            self.photo=cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)
        else:
            raise Exception("Could not get a photo.")
        self.crop()
        return

    def crop(self):
        """
        Tries to find a face in self.photo, then crops it if possible
        into self.cropped and puts the status into self.ok
        """
        height, width = self.photo.shape[:2]
        gray=cv2.cvtColor(self.photo, cv2.COLOR_BGR2GRAY)
        faces = self.__CASCADE.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags = cv2.CASCADE_SCALE_IMAGE
        )
        if len(faces)==0 or len(faces)>1:
            self.ok=False
            self.cropped=self.photo
        else:
            self.ok=True
            x, y, w, h = faces[0]
            R=self.size[1]/self.size[0]
            if h/w < R: # the face rectangle is not high enough
                y=int((R-1)*h/2)
                h=int(R*w) # so h/w is quite R
            # int() casts are necessary since cv2 uses int32 which
            # is not JSON serializable to communicate with Javascript
            self.cropRect = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
            # calculate 'a' such as 25a * 32a equals the area 2 * w * h
            a=math.sqrt(2*w*h/800)
            # upper left coordinates
            x1=round(x+w/2-12.5*a); y1=round(y+7/12*h-16*a)
            x1=int(max(x1,0)); y1=int(max(y1,0))
            # lower right coordinates
            x2=round(x+w/2+12.5*a);y2=round(y+7/12*h+16*a)
            x2=int(min(x2,width)); y2=int(min(y2,height))
            crop_img=self.photo[y1:y2, x1:x2]
            # try to normalize Hue, Saturation, Value
            hsv=cv2.cvtColor(crop_img,cv2.COLOR_RGB2HSV)
            h,s,v = cv2.split(hsv)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
            h1=h                 # same hue
            s1=s                 # same saturation
            v1 = clahe.apply(v)  # normalize the value
            hsv1=cv2.merge((h1,s1,v1))
            newimg=cv2.cvtColor(hsv1, cv2.COLOR_HSV2RGB)
            self.cropped = cv2.resize(newimg, self.size) 
        return

    @property
    def toDataUrl(self):
        """
        returns a DataUrl unicode string with self.cropped as an image
        """
        data=cv2.imencode(".jpg",self.cropped)[1].tostring()
        return (jpgPrefix+base64.b64encode(data)).decode("ascii")

    def saveAs(self, path):
        """
        saves self.cropped into a file
        @param path a path to the file system
        """
        cv2.imwrite(path, self.cropped)
        return
        
        

if __name__=="__main__":
    fi=FaceImage(sys.argv[1])
    fi.saveAs(sys.argv[2])
