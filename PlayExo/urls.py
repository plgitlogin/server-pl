 # coding: utf-8
 
from django.conf.urls import url

from . import views
from gitload.views import index

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^lti/(\w+)/$', views.lti_receiver, name='lti_receiver'),
    url(r'^pl/(?P<pltp_sha1>\w+)/(?P<pl_sha1>\w+)/$', views.pl_view, name='pl_view'),
    url(r'^pltp/(?P<pltp_sha1>\w+)/$', views.pltp_view, name='pltp_view'),
    url(r'^form/(?P<pltp_sha1>\w+)/(?P<pl_sha1>\w+)/$',views.form),
    url(r'^form/(?P<pltp_sha1>\w+)/(?P<pl_sha1>\w+)/(?P<action>reset)/$',views.form),
    url(r'^form/(?P<pltp_sha1>\w+)/(?P<pl_sha1>\w+)/(?P<action>undo)/$',views.form),
    url(r'^form/(?P<pltp_sha1>\w+)/(?P<pl_sha1>\w+)/(?P<action>grade)/$',views.form),
]


