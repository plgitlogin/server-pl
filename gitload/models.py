#!/usr/bin/env python3
import os, shutil, subprocess, git

from serverpl.settings import MEDIA_ROOT, DIRREPO

from jsonfield import JSONField

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class Repository(models.Model):
    name = models.CharField(primary_key=True, max_length=50, null = False)
    url = models.CharField(max_length=200, null = False)
    version = models.CharField(max_length=200, null = False)
    
    @staticmethod
    def add_missing_repository_in_bd():
        """ Check if every directory in 'repo/' have a corresponding entry in the db """
        for (path, subdirs, files) in os.walk(DIRREPO):    
            for filename in subdirs:
                try:
                    Repository.objects.get(name=filename)
                except Repository.DoesNotExist:
                    if (os.path.isdir(path+'/'+filename+'/.git') or os.path.isfile(path+'/'+filename+'/.git')):
                        current = os.getcwd()
                        os.chdir(path+'/'+filename)
                        url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"])
                        version = git.Repo(".").heads.master.commit.name_rev[:40]
                        os.chdir(current)
                        Repository(name=filename, version=version, url=url).save()
            break
        return False
    
    def is_repo_downloaded(self):
        return os.path.isdir(DIRREPO+'/'+self.name)



class PLTP(models.Model):
    json = JSONField()
    name = models.CharField(max_length=50, null = False)
    url =  models.CharField(max_length=360, null = False)
    sha1 = models.CharField(primary_key=True, max_length=160, null = False)
    repository = models.ForeignKey(Repository, on_delete=models.SET_NULL, null=True)
    rel_path = models.CharField(max_length=360, null = False)



class PL(models.Model):
    json = JSONField()
    name = models.CharField(max_length=100, null = False)
    sha1 = models.CharField(primary_key=True, max_length=160, null = False)
    pltp = models.ManyToManyField(PLTP)
    repository = models.ForeignKey(Repository, on_delete=models.SET_NULL, null=True)
    rel_path = models.CharField(max_length=360, null = False)

