# -*- coding: utf-8 -*-
#
#  urls.py
#  
#  Copyright 2017 Dominique Revuz <dr@univ-mlv.fr>


__author__ = 'dr'
from django.conf.urls import include, url
from sandbox import views


urlpatterns = [
    url(r'^$', views.action),
    url(r'^pl/$', views.execute),

]
