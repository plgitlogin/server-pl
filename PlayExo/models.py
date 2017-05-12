# coding: utf-8

from django.db import models
from django.contrib.auth.models import User

class studentCode(models.Model):
	student = models.CharField(max_length=100)
	student_code = models.TextField()
	pl = models.CharField(max_length=100, null = False)
	

	
