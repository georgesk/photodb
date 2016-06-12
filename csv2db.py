#!/usr/bin/python3

import sys, csv, re
import sqlite3

encodingList=[
    "utf-8",
    "latin1",
    "dos",
    "cp437",
    ]

secondNamePattern=re.compile(r"^nom$", re.I)
firstNamePattern=re.compile(r"^pr[eé]nom$", re.I)
connection=None # connection to a sqlite3 database

def find_encoding(f, encodings=encodingList):
    """
    finds the encoding of a text file
    """
    for e in encodings:
        try:
            with open(f,encoding=e) as infile:
                s=infile.read()
            return e
        except:
            pass
    return None

def getReader(csvfile):
    """
    makes a DictReader from the file f, with the given encoding.
    This Dictrader must have one field with name matched by secondNamePattern
    and another one with name matched by firstNamePattern
    @param csvfile an open string stream
    @return a Dictreader, and the names of fields for the surname and
    the given name
    """
    reader=None
    for delimiter in (";", ",", "\t",):
         csvfile.seek(0)
         reader = csv.DictReader(csvfile, delimiter=";")
         fields2=[f for f in reader.fieldnames if secondNamePattern.match(f)]
         fields1=[f for f in reader.fieldnames if firstNamePattern.match(f)]
         if (len(fields2), len(fields1)) == (1, 1):
             return reader, fields2[0], fields1[0]
    return reader, "", ""

def addToDb(row, field2, field1, verbose=False):
    """
    adds surname and given name records to the database.
    """
    c = connection.cursor()
    surname=row[field2]
    givenname=row[field1]
    c.execute("select * from person where surname=:surname and givenname=:givenname",
              {"surname": surname, "givenname": givenname})
    if c.fetchone()==None:
        ## the key surname + givenname does not yet exist !
        print("+",end="")
        sys.stdout.flush()
        c.execute("INSERT INTO person (surname, givenname) VALUES (?,?)",
                  (surname, givenname))
        connection.commit()
        return 1
    else:
        if verbose:
            print("-",end="")
            sys.stdout.flush()
    return 0

if __name__=="__main__":
    infile=sys.argv[1]
    try:
        outfile=sys.argv[2]
    except:
        outfile="db/names.db"
    connection = sqlite3.connect(outfile)
    c = connection.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS person
             (surname text, givenname text, photo text)''')
    connection.commit()
    
    encoding=find_encoding(infile)
    written=0
    with open(infile, encoding=encoding) as csvfile:
        reader, field2, field1 = getReader(csvfile)
        for r in reader:
            written=written + addToDb(r, field2, field1, verbose=True)
    print ("\n{} ==>{}\nwritten {} records".format(infile,outfile,written))
