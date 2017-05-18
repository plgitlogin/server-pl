#!/usr/bin/env/ python3
# coding: utf-8

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt

from serverpl.settings import MEDIA_ROOT

from gitload.models import PLTP,PL

import json, logging
from PlayExo.models import *

logger = logging.getLogger(__name__)




def pl_view(request, pltp_name, pl_name):
    current_tp = get_object_or_404(PLTP, name=pltp_name)
    current_pl = get_object_or_404(PL, name=pl_name)
    pl_list = current_tp.pl_set.all()
    
    info = json.loads(current_pl.json)
    query = studentCode.objects.filter(student = request.user.username, pl = pl_name)
    code = ""
    custom_code = False
    if query.first():
        custom_code = True
        code = query.first().student_code
    
    dic = {
        "info": info,
        "custom_code": custom_code,
        "code": code,
        "pl_list": pl_list,
        "pltp_name": pltp_name,
        "pl_name": pl_name,
        "username": request.user.get_full_name(),
    }
    
    return render(request, 'PlayExo/pl.html', dic)

def pltp_view(request, pltp_name):
    current_tp = get_object_or_404(PLTP, name=pltp_name)
    pl_list = current_tp.pl_set.all()
    
    info = current_tp.json
    
    return render(request, 'PlayExo/pltp.html', {
        "info": info,
        "pl_list": pl_list,
        "pltp_name": pltp_name,
        "username": request.user.get_full_name(),
    })

@csrf_exempt
def lti_receiver(request, sha1):
    if (not request.user.is_authenticated):
        return HttpResponse('User not authenticated throught LTI', status=401)
        
    pltp = get_object_or_404(PLTP, sha1=sha1)
    
    return redirect(pltp_view, pltp.name)
        
