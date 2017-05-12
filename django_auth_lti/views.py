from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def lti_launch_request_receiver(request):
    current_user = request.user

    return render(request, 'django_auth_lti/lti.html', {
        'username': current_user.username,
        'user_firstname': current_user.first_name,
        'user_lastname': current_user.last_name,
        'user_email': current_user.email,
    })
