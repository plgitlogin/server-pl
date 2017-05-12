
from django.shortcuts import render,get_object_or_404
from django.template import loader
from django.http import HttpResponse,Http404

from mysite.settings import MEDIA_ROOT, PROJECT_DIR
from gitload.models import *
from PlayExo.models import *
from shutil import copyfile

import json, os, logging

logger = logging.getLogger(__name__)


def execute(request, pltp_name, pl_name):
    
    pltp_lst = Loaded_Pltp.objects.order_by('name')
    current_tp = get_object_or_404(Loaded_Pltp, name=pltp_name)
    pl_lst = current_tp.loaded_pl_set.all()
    
   
    code = request.POST.get("code", "")
    
    #save code --------
    query = studentCode.objects.filter(student = request.user.username, pl = pl_name)
    if not query.first():
        print("--------create ----------")
        new_instance = studentCode(student = request.user.username, student_code = code, pl = pl_name)
        new_instance.save()
    else:
        print("--------edit ----------")
        query.first().student_code = code
	
    
    # ----------------
    
    current_pl = get_object_or_404(Loaded_Pl, name=pl_name)
    
    stu = open(PROJECT_DIR+"/../"+"sandbox/env/student.py", "w")
    stu.write(code)
    stu.close()
    
    for filename in ["grader.py","plutils.py","testcode.py","utils.py","pl.json"]:
        try:
            copyfile(MEDIA_ROOT+"/"+current_pl.dirname+"/"+filename, PROJECT_DIR+"/../"+"sandbox/env/"+filename)
        except:
            logger.info(filename + " missing")
        
    os.chdir(PROJECT_DIR+"/../sandbox/env")

# import subprocess
#  exectutiondict = subproces.run('python3', "grader.py", ) 
    os.system('{} {} {} {}'.format('python3', "grader.py", ">", "res.json"))
    
    with open(PROJECT_DIR+"/../"+"sandbox/env/res.json") as datafile:
        context = json.load(datafile)
    
    context["feedback"] = context["feedback"].replace("<br>", "\n")
    context["tp_lst"] = pltp_lst
    context["pl_lst"] = pl_lst
    context["pltp_name"] = pltp_name
    context["index"] = False
    context["pl_id"] = -1
    context["pltp_id"] = -1
    context["is_result"] = 1



    return render(request, 'PlayExo/default_struct.html', context)


