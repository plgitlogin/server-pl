#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#

import os, shutil, git, subprocess, logging

from serverpl.settings import DIRREPO

from os.path import basename, isfile, isdir, splitext, dirname, realpath

from gitload.loader import PLTP_Loader
from gitload.models import Repository


logger = logging.getLogger(__name__)


class Browser():
    
    def __init__(self, repository, dic = None):
        """ Members will be initialized with a dictionnary if provided """
        
        if (not dic):
            self.name = repository.name             #Name of the repository
            self.url = repository.url               #URL of the repository
            
            self.root = DIRREPO + '/' + self.name   #Absolute path to the local copy of the repository
            self.current_path = self.root           #Absolute path to the actual directory of the repository in the browser
            self.pltp_list = list()                 #List of every pltp in self.current_path
            self.dir_list = list()                  #List of every directory in self.current_path
            self.other_list = list()                #List of every other files in self.current_path
            
            if (not repository.is_repo_downloaded()):
                self.get_repo()
            else:
                repo = git.Repo(self.root)
                self.version = repo.heads.master.commit.name_rev[:40]
            
        else:
            for k, v in dic.items():
                setattr(self, k, v)
    
    def get_repo(self):
        """ Create or replace self.path with a new clone of self.url
            Update self.version """

        if (isdir(self.root)):
            shutil.rmtree(self.root)
        os.mkdir(self.root)
        
        repo = git.Repo.init(self.root)
        
        origin = repo.create_remote('origin', self.url)
        try:
            origin.fetch()
        except:
            logger.info("Couldn't join "+self.url)
            return False;
        
        origin.pull(origin.refs[0].remote_head)
        self.version = repo.heads.master.commit.name_rev[:40]
        repo_object = Repository.objects.get(name=self.name)
        repo_object.version = self.version
        repo_object.save()
        
        return True
    
    
    def refresh_repo(self):
        """ Refresh the local copy of the repo by checking difference and doing a checkout if found any """
        if (not isdir(self.root) or not isdir(self.root + "/.git")): #Check if the repo is already cloned
            self.get_repo()
            return
        
        repo = git.Repo.init(self.root)
        
        origin = repo.remote()
        try:
            origin.fetch()
        except git.exc.CommandError:
            logger.info("Couldn't join " + self.url + ", stopping refresh")
            return
            
        if (repo.index.diff(None)):
            self.get_repo()
            self.current_path = self.root
    
    
    def parse_content(self):
        """ Fill 'pltp', 'dir' and 'other' lists with the corresponding file. """
        print("CURRENT_PATH: " + self.current_path)
        for (path, subdirs, files) in os.walk(self.current_path):
            for filename in files:
                if (os.path.splitext(filename)[1] == '.pltp'):
                    self.pltp_list.append(filename)
                else:
                    self.other_list.append(filename)
                    
            for filename in subdirs:
                if (filename[0] != '.'):
                    self.dir_list.append(filename)
            break;
    
    def load_pltp(self, rel_path, repository):
        """ Create a PLTP_Loader with the rel_path to the local repo of a pltp """
        loader = PLTP_Loader(rel_path, repository)
        return loader.load()
        
    def cd(self, rel_path = "/"):
        """ Change self.current_path, rel_path is relative to self.root """
        if (rel_path == "/" or rel_path == "~"):
            self.current_path = self.root
            
        elif (isdir(self.root + "/" + rel_path)):
            self.current_path = self.root + "/" + rel_path
            if (self.current_path[-1] != "/"):
                self.current_path += "/"
