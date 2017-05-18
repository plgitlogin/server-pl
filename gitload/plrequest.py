#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  request.py
#  
#  Copyright 2017 Dominique Revuz <dr@univ-mlv.fr>
#  

__doc__ = """

    Ce fichier a pour objectif de gérer les communications
    avec la sandbox.
    """

import requests, zipfile, pathlib, subprocess, hashlib, os
import gitload.question


def pllogdata(user, sha1, studentfile=None, mode="try", url = "http://127.0.0.1:9090"):
    if studentfile == None:
        mode= "start"
    geturl=url+"/add/tt"
    posturl=url+"/add/xx"
    try:
        csrftoken = requests.get(geturl).cookies['csrftoken']
        header = {'X-CSRFToken': csrftoken}
        cookies = {'csrftoken': csrftoken}
        r=requests.post(posturl,headers=header, cookies=cookies,data={"user":user,"code":studentfile,"mode":mode,"sha1":sha1})
    except Exception as e:
        print(" Berk can't access pldata",e) # don't dye for this
        r=None
    return r



class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)



class SanboxSession:
    def __init__(self,question,url,studentfile):
        self.question = question
        self.url = url
        self.studentfile = studentfile

    def createEnvZipRun(self):
        from shutil import rmtree
        rmtree('/tmp/env/', ignore_errors=True)
        p=pathlib.Path('/tmp/env/')
        p=self.question.createdir(self.studentfile)
        self.zipname = str(p.resolve() /  "env.zip")
        with cd(str(p)) :
            subprocess.run(['zip','-qjr','env.zip','.'])
            
    def checkgrader(self):
        self.question.checkgrader()

    def call(self):
        mn = self.createEnvZipRun()
        self.checkgrader()
        mn = hashlib.sha1()
        zipvalue=open(self.zipname, 'rb').read()
        mn.update(zipvalue[:])
        self.hashvalue = mn.hexdigest()
        self.files = {
            'environment': zipvalue,
            'student.py': self.studentfile,
            "grader.py": self.question.dico['grader'],
            'hashvalue': self.hashvalue,
        }
        #~ pllogdata(-1,self.hashvalue, self.studentfile)
        return (requests.post(self.url, data=self.question.dico, files=self.files, timeout=1000).json(), self.hashvalue, self.question.dico)

