
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse,Http404

from uuid import uuid4
import json
import os
import zipfile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import subprocess




class Executor:
    def __init__(self,request):
        self.containername = None
        # New DIR
        unique=str(uuid4())
        path = default_storage.save(unique+"/environment.zip", ContentFile(request.FILES['environment'].read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        self.dirname = os.path.join(settings.MEDIA_ROOT, unique)
        zip_ref = zipfile.ZipFile(tmp_file, 'r')
        zip_ref.extractall(self.dirname)
        zip_ref.close()

        

    def execute(self):
        os.chdir(self.dirname)
        try:
            xx = subprocess.check_output(['python3','grader.py'])
        except Exception as e:
            errormessage={"feedback":" Erreur de la plateforme \npassez à lexercice suivant\nMerci de votre compréhension\n","success":True}
            dico_response = {"platform_error":[str(e)] ,"grade":errormessage}
            os.chdir("..")
            return json.dumps(dico_response)
        os.chdir("..")
        return xx

def letsrock(request):
    executor=Executor(request)
    
    tutu=executor.execute()
    print("############################")
    print(tutu)
    dico_response = {"platform_error":[] ,"grade":"xxx"}
    return HttpResponse(json.dumps(dico_response))

"""
def buildDockerInvocation():
    ["docker","run","-v",HostPath+":"+InnerPath+":rw","-a", "stdin","-a","stdout","-a","stderr"].append(Env_Var).append(["--rm=true", "--net=none","-m",memlimit,"--cpu-shares", CPU_SHARES,"--cpu-period",CPU_PERIOD,"--cpu-quota",CPU_QUOT,"-v",SFTP_PATH+":"+SFTP_INNER_PATH+":ro","--name",CONTAINER_NAME","execute_in_environment",
"""
