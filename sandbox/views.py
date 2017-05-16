__author__ = 'dr'


from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse,Http404
from sandbox.executor import letsrock

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def execute(request):
	if request.META["REQUEST_METHOD"] != "POST":
		return HttpResponse('{"error":"Access must be POST"}')


	for key in ['environment', 'grader.py', 'student.py']:
		if not key in request.FILES:
			return HttpResponse('{"error":"Absence de la clef '+key+'"}')

	return HttpResponse(letsrock(request))


@csrf_exempt
def action(request):
	if "action" in request.GET:
		l = request.GET["action"]
	elif "action" in request.POST:
		l = request.POST["action"]
	else:
		return HttpResponse('{"error":"No action defined"}')
	if l == "languages":
		return HttpResponse('{"languages":["c","python"]}')
	if l == "version":
		return HttpResponse('{"version":"pysandbox-0.1"}')
	if l != "execute":
		message = '{"error":"unkown action :'+ l+'"}'
		return HttpResponse(message)
	# let's do the job from Here on
	
	return execute(request)
