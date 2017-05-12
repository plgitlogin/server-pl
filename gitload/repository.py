#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#

import os,shutil,git

from serverpl.settings import DIRREPO

from os.path import basename, isfile, isdir, splitext

from gitload.base import PLTP_Loader

class Repository():
    
    def __init__(self, repo_url, dic = None):
        """ Members will be initialized with a dictionnary if provided """
        
        if (not dic):
            self.url = repo_url                             #URL of the remote repo
            self.name = splitext(basename(repo_url))[0]     #Name of the repo ('plbank' for isntance)
            self.actif = 0                                  #Number of active PLTP in the repo
            self.version = ''                               #First seven number of the last commit
            
            self.local_root = DIRREPO+ '/' + self.name   #Absolute path to the local copy of the repository
            self.local_current_path = self.local_root       #Absolute path to the actual directory of the repository in the browser
            self.local_pltp_list = list()                   #List of every pltp in self.local_root
            self.local_dir_list = list()                    #List of every directory in self.local_root
            self.local_other_list = list()                  #List of every other files in self.local_root
        else:
            for k, v in dic.items():
                setattr(self, k, v)
    
    
    def get_repo(self):
        """ Create or replace self.local_path with a new clone of self.url """
        if (isdir(self.local_root)):
            shutil.rmtree(self.local_root)
        os.mkdir(self.local_root)
        
        repo = git.Repo.init(self.local_root)
        
        origin = repo.create_remote('origin', self.url)
        try:
            origin.fetch()
        except:
            logger.info("Couldn't join "+self.url)
            return False
        
        origin.pull(origin.refs[0].remote_head)
        return True
    
    
    def refresh_repo(self):
        """ Refresh the local copy of the repo by checking difference and doing a checkout if found any """
        if (not isdir(self.local_root) or not isdir(self.local_root + "/.git")): #Check if the repo is already cloned
            self.get_repo()
            return
        
        repo = git.Repo.init(self.local_root)
        
        origin = repo.remote()
        try:
            origin.fetch()
        except git.exc.CommandError:
            logger.info("Couldn't join " + self.url + ", stopping refresh")
            return
            
        if (repo.index.diff(None)):
            gitco = repo.git
            gitco.checkout('master', '.')
            if (not isdir(self.local_current_path)):
                self.local.current_path = self.local_root
    
    
    def parse_content(self):
        """ Fill 'pltp', 'dir' and 'other' lists with the corresponding file. """
        for (path, subdirs, files) in os.walk(self.local_current_path):
            for filename in files:
                if (os.path.splitext(filename)[1] == '.pltp'):
                    self.local_pltp_list.append(filename)
                else:
                    self.local_other_list.append(filename)
                    
            for filename in subdirs:
                if (filename[0] != '.'):
                    self.local_dir_list.append(filename)
            break;
    
    def load_pltp(self, rel_path):
        """ Create a PLTP_Loader with the rel_path to the local repo of a pltp """
        repo = git.Repo(self.local_root)
        version = repo.heads.master.commit.name_rev
        
        loader = PLTP_Loader(self.local_root, rel_path, version)
        loader.load()
        return loader
    
    def load_many_pltp(self, *args):
        """ Create a PLTP_Loader with the rel_path to the local repo of a pltp """
        repo = git.Repo(self.local_root)
        version = repo.heads.master.commit.name_rev
        
        for path in args:
            PLTP_Loader(self.local_root, path, version).load()
        
    def cd(self, rel_path = "/"):
        """ Change self.local_current, rel_path is relative to self.local_root """
        if (rel_path == "/" or rel_path == "~"):
            self.local_current_path = self.local_root
            
        elif (isdir(self.local_root + "/" + rel_path)):
            self.local_current_path = self.local_root + "/" + rel_path
            if (self.local_current_path[-1] != "/"):
                self.local_current_path += "/"
