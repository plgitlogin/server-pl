import os, shutil

from mysite.settings import MEDIA_ROOT

from jsonfield import JSONField

from django.db import models



class Loaded_Pltp(models.Model):
    json = JSONField()
    name = models.CharField(max_length=50, null = False)
    url =  models.CharField(max_length=360, null = False)
    sha1 = models.CharField(max_length=160, null = False)

class Loaded_Pl(models.Model):
    json = JSONField()
    name = models.CharField(max_length=100, null = False)
    sha1 = models.CharField(max_length=160, null = False)
    pltp = models.ManyToManyField(Loaded_Pltp)
