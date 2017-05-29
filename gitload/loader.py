#!/usr/bin/env python3
# encoding: utf-8
# Copyright Dominique Revuz, Quentin Coumes 2017

import os, sys, shutil, git, re, json, time, logging, subprocess, pathlib, hashlib

from os.path import basename, isfile, isdir, splitext

from gitload.models import PLTP, PL

from pysrc.question import Question, ErrorPL

from serverpl.settings import SANDBOX_URL, DIRREPO

from django.conf import settings
from django.core.files.storage import Storage



class NotChecked(Exception):
    pass


class PL_Loader():
    """Handle the loading of a PL by checking its integrity and loading it into the database. """
    def __init__(self, rel_path, repository):
        self.name = splitext(basename(rel_path))[0]
        self.rel_path = rel_path
        self.repository = repository
        self.sha1 = self._get_sha1()
        self.root = DIRREPO+'/'+repository.name
        self.dic = None
        
            
    def load(self, pltp, force = False):
        """ Load the PL by checking its integrity and adding it to the database.
        Return (True, None) if the PL was correctly loaded, (False, error_message)
        if something wrong happened. """
        try:
            q= Question(self.rel_path, self.root)
            self.dic = q.dico
            self.zipvalue = q.getZipValue()
        except ErrorPL as e:
            return False, "Impossible de charger "+self.rel_path+": "+str(e)
        
        self._add_to_db(pltp, force)
        
        return True, None
    
    def _get_sha1(self):
        """ Create a sha1 with the name of the PL and the name+version of the git containing it """
        hasher = hashlib.sha1()
        hasher.update((self.name+self.repository.name).encode('utf-8'))
        return hasher.hexdigest()
    
    def _add_to_db(self, pltp, force):
        """ Add the PL to the database if none with the same sha1 already exists. """
        try:
            pl = PL.objects.get(sha1=self.sha1)
            if force:
                pl.delete()
                raise PL.DoesNotExist
        except PL.DoesNotExist:
            pl = PL(name=self.name, sha1=self.sha1, json= self.dic, repository=self.repository, rel_path=self.rel_path)
            pl.save()
        pl.pltp.add(pltp)



class PLTP_Loader():
    """Handle the loading of a PLTP by checking its integrity and its PL integrity and loading them into the database. """
    def __init__(self, rel_path, repository):
        self.name = splitext(basename(rel_path))[0]
        self.rel_path = rel_path
        self.repository = repository
        self.sha1 = self._get_sha1()
        self.root = DIRREPO+'/'+repository.name
        self.url = "/PlayExo/lti/"+self.sha1
        self.dic = None
        self.pl = None
        
    def load(self, force=False):
        """ Load the PLTP by checking its integrity and adding it and every self.pl to the database.
        Return:
            - (sha1, None) if the PLTP was loaded
            - (None, error_msg) if PLTP couldn't be loaded
            - (None, None) if PLTP is already loaded
        """
        try:
            self.dic = Question(self.rel_path, self.root).dico
        except ErrorPL as e:
            return None, "Impossible de charger "+self.rel_path+": "+e.message
        if not self._add_to_db(force):
            return None, None
        
        pltp = PLTP.objects.get(sha1=self.sha1)
        self.pl = self._get_pl_list()
        if (not self.pl):
            pltp.delete()
            return None, "Erreur: Impossible de récuperer la liste des PL associés à "+self.rel_path
            
        for pl in self.pl:
            loaded, error = pl.load(pltp, force)
            if (not loaded):
                pltp.delete()
                return None, error
            
        return self.sha1, None
        
    def _get_sha1(self):
        """ Create a sha1 with the name of the PLTP and the name+version of the git containing it """
        hasher = hashlib.sha1()
        hasher.update((self.name+self.repository.name).encode('utf-8'))
        return hasher.hexdigest()
    
    def _get_pl_list(self):
        """ Return the list of every PL_Loader needed by this pltp """
        pltp = open(self.root+self.rel_path, "r")
        pl_list = list()
        for line in pltp:
            if (line[0] == '@'):
                i=1
                while line[i]==' ':
                    i=i+1
                filename=line[i:-1]
                pl_list.append(PL_Loader(filename, self.repository))
        pltp.close()
        return pl_list
    
    def _add_to_db(self, force):
        """ Try to add the PLTP to the database, return True if the PLTP was created, 
        if force = False, return False if one with the same sha1 already exists, else load it anyway."""

        try:
            existing = PLTP.objects.get(sha1=self.sha1)
            if (force):
                existing.delete()
                raise PLTP.DoesNotExist
        except PLTP.DoesNotExist:
            pltp = PLTP(name=self.name, url=self.url, sha1=self.sha1, json=self.dic, repository=self.repository, rel_path=self.rel_path)
            pltp.save()
            return True
        return False
        pass

