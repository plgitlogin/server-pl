 # coding: utf-8
 
from django.conf.urls import url

from . import views
from gitload.views import index

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^lti/(\w+)/$', views.lti_receiver, name='lti_receiver'),
    url(r'^pl/(\w+)/(\w+)/$', views.pl_view, name='pl_view'),
    url(r'^pltp/(\w+)/$', views.pltp_view, name='pltp_view'),
]
