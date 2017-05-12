#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Question.py
#  
#  Copyright 2017 Dominique Revuz <dr@univ-mlv.fr>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


import os, re, json, time
from pathlib import Path


def openandsplit(filename):
    try:
        return open(filename,"r").read().split("\n")
    except IOError as e:
        print(e)
        import sys
        sys.exit(1)


name='^(?P<name>\w*)\s*'
operator='(?P<op>=|==|=@)\s*'
value='(?P<value>[^\s=@#]*)'
commentANDend='($|(?P<comment>#.*)$)'
li=re.compile(name+operator+value+commentANDend)#,re.DEBUG)
starmulti=re.compile("^(?P<name>\w*)\s*(?P<op>==).*$")#,re.DEBUG)
debug=False


def parseOneLine(line,d):
    if line =="" or line.startswith("#"):
        return (False,None)
    if debug:
        print("{{"+line+"}}")
    xx = li.search(line)
    if xx == None:
        if debug:
            print("problème  de format avec la ligne :"+line)
        xx== starmulti.search(line)
        if xx == None :
            if debug:
                print("problème  :"+line)
            return False,None
    if xx.group("op")== "==":
        return (True,(xx.group("name")))
    elif xx.group("op")== "=@":
        if not "files" in d:
            d['files']=[]
        d['files'].append(xx.group("value"))
    elif xx.group("op")== "=":
        if xx.group("name") in d:
            print("Error nom déja défini")
        d[xx.group("name")]=xx.group("value")
    return (False,None)

def parse(filename,currentdict=None):
    """
    parse filename for values pairs adding them to currendict
    """
    currendict = {} if currentdict == None else currentdict
    multi = False
    for line in openandsplit(filename):
        # in multi line 
        if multi :
            # end of multi line 
            if line=="==" : 
                currentdict[multiname]=multivalue
                multi = False
                multiname = None
            else: # in multi line 
                multivalue += line + "\n"
        else:
            multi,multiname = parseOneLine(line,currentdict)
            multivalue=""
    return currentdict

def makepath(plname,root):
    """
    concat with a unique / in between
    """
    
    if ((root.endswith('/') and (not plname[0] =='/')) or (not root.endswith('/') and  plname[0] =='/')) :
        return root+plname
    elif (root.endswith('/') and plname[0] =='/'):
        return root+plname[1:]
    else:
        return root+"/"+plname



class Question:
    def __init__(self,filename,root=None):
        """
        load a local.pl file into a question
        and save it
        root is the top directory in repository 
        """
        if root == None and not "root" in os.environ:
            raise Error(" No root defined")
        dico={"url":filename+"_"+os.path.basename(root)}
        parse(makepath(filename,root),dico)
        #printdico(dico)
        ### Appel récursif sur le template 
        while "template" in dico:
            templatename = dico['template']
            if not templatename.endswith(".pl") :
                templatename += ".pl"
            del dico['template'] # on boucle sur les templates
            dico = parse(root+templatename,dico)
        # read the files
        if 'files' in dico:
            dico["basefiles"]={}
            l = dico['files']
            del dico['files']
            for x in l:
                name = os.path.basename(x)
                if name in dico:
                    perror("le nom ",name, " est déja défini ")
                try:
                    f= open(makepath(x,root),"r")
                    dico["basefiles"][name]=f.read()
                except Exception as e:
                    print(e)
                    print("le fichier de la directive files",makepath(x,root),"ne peut être ouvert")
                    raise
                    # Exception("Format de fichier pl "+filename+" incorrect")
        self.dico = dico
        self.json = json.dumps(dico)
        self.filename = filename
        self.qname = "/tmp/"+os.path.basename(filename)+str(time.time())

    def createdir(self,studentfilestr,pathdir=None):
        """
        creation of the directory for the execution of the grading 
        action
        1) creating files from pl elements
        2) saving file from the pldict
        3) save student file 
        """
        if studentfilestr == None and not "student.py" in self.dico and not "student" in self.dico:
                        raise Error("creatDir needs the student file ")
        if "student" in self.dico:
            studentfilestr=self.dico["student"]
        elif "student.py" in self.dico:
            studentfilestr=self.dico["student.py"]
        if pathdir == None :
            pathdir = Path('/tmp/env/'+str(time.time()))
        pathdir.mkdir(parents=True)
        # 1
        for name,trad in [('grader','grader.py'),('soluce','soluce.py'),('inputgenerator','inputgenerator.py')]:
            if name in self.dico:
                with pathdir.joinpath(trad).open(mode="w") as f:
                    print(self.dico[name],file=f)
        # 2
        if "basefiles" in self.dico:
            for thefile in self.dico["basefiles"].keys():
                with pathdir.joinpath(thefile).open(mode="w") as f:
                        print(self.dico["basefiles"][thefile],file=f)
        # directory ready to run only the stduent's file is missing
        # 3
        with  pathdir.joinpath("student.py").open(mode="w") as f:
                    print(studentfilestr,file=f)
        if debug :
            for k,v in self.dico.items():
                print(k+" == " )
        if "basefiles" in self.dico:
            del self.dico["basefiles"]
        self.pdir = pathdir
        with pathdir.joinpath("pl.json").open(mode="w") as f:
            json.dump(self.dico,fp=f)
        print("exercice sauvegardé dans "+str(self.pdir))
        return self.pdir

    def checkgrader(self):
        if not "grader" in self.dico:
            if not "basefiles" in self.dico :
                raise Error("No grader")
            else:
                if not "grader.py" in self.dico["basefiles"]:
                    raise Error("No grader")
                else:
                    self.dico["grader"]=self.dico["basefiles"]["garder.py"]

class ErrorPL(Exception):
    pass


def printdico(d):
    for k in d.keys():
        if type(d[k]) == str :
            print(k,"=",d[k][0:30])
        elif type(d[k]) == list :
            print(k,"==",d[k][0])
        elif type(d[k]) == dict :
            for kk in d[k].keys():
                print(d[k][kk])
        else:
            print("Type étrange ")



if __name__ == '__main__':
    print("not a cli action")

