#!/usr/bin/python3
import sqlite3
from odf.opendocument import load
from odf import text, table, draw
import os, os.path

class Person:
	def __init__(self, surname, givenname, photo, classe):
		self.surname=surname
		self.givenname=givenname
		self.photo=photo
		self.classe=classe
		return

	def __str__(self):
		return "Personne(surname={surname}, givenname={givenname}, photo={photo}, class={classe})".format(**self.__dict__)
	
	def photo_retouchee(self):
		result="nobody.jpg"
		if self.photo:
			filename=self.photo.replace("photos/","")
			result=os.path.join("photos_retouchees", filename)
			if os.path.exists(result):
				return result
			else:
				result=os.path.join("photos_retouchees", 
									 "erreurs","corrections",filename)
				if os.path.exists(result):
					return result
		return result
		
nobody=Person("","",None,None)
blanc=Person("","","photos/blanc.jpg",None)

def trombinoClasse(nomClasse, cursor):
	"""
	crée un document de trombinoscope pour un classe
	@param nomClasse le nom de la classe
	@param cursor un curseur pour la base de donnée des élèves
	photographiés
	"""
	data=[]
	query="select * from person where class='{}' \
	       order by surname, givenname".format(nomClasse)
	for row in c.execute(query):
		data.append(Person(*row))


	doc = load("template.odt")
	headers=doc.getElementsByType(text.H)
	tables=doc.getElementsByType(table.Table)

	photos=[p for p in os.listdir("photos_retouchees") if ".jpg" in p]
	for h in headers:
		h.addText("Trombinoscope : "+nomClasse)
	counter=0
	for t in tables:
		paras=t.getElementsByType(text.P)
		for p in paras:
			if counter < len(data):
				person=data[counter]
			else:
				person=blanc
			nomprenom="{} {}".format(person.surname, person.givenname)
			p.addText(nomprenom)
			imgs=p.getElementsByType(draw.Image)
			i=imgs[0]
			i.setAttribute("href","../"+person.photo_retouchee())
			counter +=1

	doc.save(nomClasse,True)
	print("enregistré {}.odt".format(nomClasse))
	
def getClasses(cursor):
	"""
	renvoie une liste de classes existantes dans la base de données
	@param curseur un curseur pour la base de données
	@return une liste ordonnée de classes (non nulles)
	"""
	classes=cursor.execute("select distinct class from person").fetchall()
	classes=set([cl[0].strip() for cl in classes if cl[0]])
	classes=list(classes)
	classes.sort()
	return classes
	

if __name__=="__main__": 
	conn = sqlite3.connect('db/names.db')
	c = conn.cursor()
	for cl in getClasses(c):
	    trombinoClasse(cl,c)
