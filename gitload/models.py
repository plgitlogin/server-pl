import os, shutil

from serverpl.settings import MEDIA_ROOT, DIRREPO

from jsonfield import JSONField

from django.core.exceptions import ObjectDoesNotExist
from django.db import models



class Loaded_Pltp(models.Model):
    json = JSONField()
    name = models.CharField(max_length=50, null = False)
    url =  models.CharField(max_length=360, null = False)
    sha1 = models.CharField(primary_key=True, max_length=160, null = False)

class Loaded_Pl(models.Model):
    json = JSONField()
    name = models.CharField(max_length=100, null = False)
    sha1 = models.CharField(primary_key=True, max_length=160, null = False)
    pltp = models.ManyToManyField(Loaded_Pltp)

class Repository(models.Model):
    name = models.CharField(primary_key=True, max_length=50, null = False)
    url = models.CharField(max_length=200, null = False)
    
    @staticmethod
    def missing_repository_in_bd():
        """ Check if every directory in 'repo/' have a corresponding entry in the db """
        for (path, subdirs, files) in os.walk(DIRREPO):    
            for filename in subdirs:
                try:
                    Repository.objects.get(name=filename)
                except Repository.DoesNotExist:
                    return True
            break
        
        return False
        
    def is_repo_downloaded(self):
        return os.path.isdir(DIRREPO+'/'+self.name)
