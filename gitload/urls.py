# coding: utf-8

# DJANGO IMPORTS
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^browse/$', views.browse),
    url(r'^view_file/$', views.view_file),
    url(r'^loaded_pltp/$', views.loaded_pltp),
]
