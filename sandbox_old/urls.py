# -*- coding: utf-8 -*-
#
#  urls.py
#  
#  Copyright 2017 Dominique Revuz <dr@univ-mlv.fr>


__author__ = 'dr'
from django.conf.urls import include, url
from sandbox import views


urlpatterns = [
    url(r'^(?P<pltp_name>\w+)/(?P<pl_name>\w+)/pl/$', views.execute),
    
]
