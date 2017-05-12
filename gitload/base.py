# coding: utf-8

import os, sys, shutil, git, re, json, time, logging, subprocess, pathlib, hashlib

from os.path import basename, isfile, isdir, splitext



from gitload.models import Loaded_Pltp, Loaded_Pl
from gitload.plrequest import SanboxSession
from gitload.question import Question, ErrorPL
from gitload.settings import SANDBOX_URL

from django.conf import settings
from django.core.files.storage import Storage


logger = logging.getLogger(__name__)



class PLTP_Loader():
    
    def __init__(self, repo_root, rel_path_pltp, version):
        self.root = repo_root       #Path to the local repository
        self.pltp = rel_path_pltp   #Path to the pltp relative to self.root
        self.version = version      #Version Git du pltp
        self.pl = list()            #List of the [pl, sha1, dic] corresponding to pltp
        
    def load(self):
        """ Call this function to load the PLTP. """
        pltp_name = splitext(basename(self.pltp))[0]
        pltp = Loaded_Pltp.objects.filter(name=pltp_name) #Delete the pltp with the same name in the DB, if it exists.
        if (pltp):
            for tmp in pltp:
                tmp.delete()
                
        self._check_pltp();        
        
        self.pl = self._get_pl_list()
        for pl in self.pl:
            pl[1], pl[2] = self._check_pl(pl[0])
        self._add_to_db()
    
    
    def _add_to_db(self):
        """Add the path to the pltp and the jsons in the database """
        
        pltp_name = splitext(basename(self.pltp))[0]
        pltp_json = self._parse_pltp(self.root+self.pltp)
        hasher = hashlib.sha1()
        hasher.update((pltp_name+self.version).encode('utf-8'))
        sha1 = hasher.hexdigest()
        url = "/PlayExo/lti/" + sha1
        
        pltp = Loaded_Pltp(name = pltp_name, sha1=sha1, json = pltp_json, url=url)
        pltp.save()
        
        for pl in self.pl:
            pl_name = splitext(basename(pl[0]))[0]
            pl_json = json.dumps(pl[2])
            sha1 = pl[1]
            
            pl = Loaded_Pl.objects.filter(sha1=pl[1])
            if (not pl): #Create the pl in the DB if it doesn't exists
                pl = Loaded_Pl(name = pl_name, sha1 = sha1, json = pl_json)
                pl.save()
            else:
                pl = pl[0]
            pl.pltp.add(pltp)


    def _check_pltp(self, sandboxurl=SANDBOX_URL):
        print("Test de "+self.pltp+"\nsur : "+sandboxurl)
        dico = self._parse_pltp(self.root+self.pltp)
        for key in ["introduction", "concept", "name"]:
            if not key in dico:
                raise ErrorPL("PLTP sans balise "+key)
        
        missing_list = self._check_pl_exist()

        if (missing_list):
            raise ErrorPL("PL missing: " + str(missing_list))
        return True
    
    
    def _get_pl_list(self):
        """ Return the list of every pl needed by this pltp """
        pltp = open(self.root+self.pltp, "r")
        pl_list = list()
        for line in pltp:
            if (line[0] == '@'):
                pl_list.append([line[2:-1], "", dict()])# FIXME plusieurs espaces 
        pltp.close()
        return pl_list
    
    
    def _check_pl_exist(self):
        """ Return the list of every missing pl for this pltp, return None if all exist """
        missing_list = list()
        for pl in self.pl:
            if (not os.path.exists(self.root +'/'+ pl[0])):
                missing_list.append(pl[0])
        if (missing_list):
            return missing_list
        return None
    
    @staticmethod
    def _parse_pltp(path):
        f = open(path, "r")
        dic = {}    
        tag = ""
        dic[tag] = []
        active_tag = False
        
        for line in f:
            if(("=" in line) and (line.count('=') == 1) and (not active_tag)):
                tag, value = line.split('=')
                dic[tag] = value
            elif("==" in line and (not active_tag)):
                active_tag = True
                tag, value = line.split('==')
                dic[tag] = [value]
            elif("==" in line):
                active_tag = False
            elif (active_tag):
                dic[tag].append(line.replace("\n", ""))
                    
        return dic
    
    def _check_pl(self, pl, sandboxurl=SANDBOX_URL, studentfile="print(3000)"):
        print("Test de "+pl+"\nsur : "+sandboxurl)
        q=Question(pl,root=self.root)
        print("Question chargée") 
        if "testcode" in q.dico:
            studentfile=q.dico["testcode"]
        elif "soluce" in q.dico :
            studentfile=q.dico["soluce"]
        result, sha1, dic = SanboxSession(q,sandboxurl,studentfile).call() # question,url,studentfile
        if (result["platform_error"]):
            raise ErrorPL("Erreur lors du test de " + pl + ": " + str(result["platform_error"]))
        return sha1, dic
