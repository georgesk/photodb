#!/usr/bin/python3

import sqlite3, sys, os
from subprocess import call

def unquote(s):
    if len(s)<2: return s
    elif s[0]=='"' and s[-1]=='"': return s[1:-1]
    elif s[0]=="'" and s[-1]=="'": return s[1:-1]
    else: return s
    
def protege(s):
	return s.replace(" ","-").replace("'","-")    

def sansAccent(s):
    accent={'a':'àâ','e':"éèêë","i":"îï","o":"ô","u":"ù","c":"ç",'A':'ÀÂ',
    'E':"ÉÈÊË","I":"ÎÏ","O":"Ô","U":"Ù","C":"Ç"}
    r=""
    for c in s:
        ok=False
        for d in accent.keys():
            if c in accent[d]:
                r+=d
                ok=True
        if not ok:
            r+=c
    return r

def usage():
    print("""Usage : {} <nom de répertoire>

Exporte des photos au format demandé par pronote dans un répertoire
""".format(sys.argv[0]))
    return

if __name__=="__main__":
    outdir=None # répertoire où envoyer les résultats
    if len(sys.argv)<2:
        usage()
        sys.exit(1)
    else:
        outdir=sys.argv[1]
        os.makedirs(outdir, mode=0o755, exist_ok=True)
    conn=sqlite3.connect("/var/lib/photodb/db/names.db")
    c=conn.cursor()
    c.execute("select * from person")
    for p in c:
        nom=p[0]
        prenom=p[1]
        if p[2] and nom and prenom:
            fichier=p[2].replace("photos/","")
            nouveauFichier=protege(sansAccent(prenom)).lower()+"."+protege(sansAccent(nom)).lower()
            cmd="cp /var/lib/photodb/photos/%s %s/%s.jpg" %(fichier, outdir, nouveauFichier)	
            call(cmd, shell=True)
		
	
