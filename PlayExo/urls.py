 # coding: utf-8
 
from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^lti/(\w+)/$', views.lti_receiver, name='lti_receiver'),
    url(r'^pl/(?P<pltp_name>\w+)/(?P<pl_name>\w+)/$', views.pl_view, name='pl_view'),
    url(r'^pltp/(?P<pltp_name>\w+)/$', views.pltp_view, name='pltp_view'),
]
