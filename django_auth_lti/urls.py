# coding: utf-8

# DJANGO IMPORTS
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views. lti_launch_request_receiver),
]
