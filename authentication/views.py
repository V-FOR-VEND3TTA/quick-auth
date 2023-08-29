from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .models import Verification
from helpers import send_mail
from django.contrib.sites.models import Site


# Create your views here.
def register(request):

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        User.objects.create_user(email=email, username=email, password=password)
        user = User.objects.get(username=email)

        Verification(user_id=user.id).save()
        v = Verification.objects.get(user_id=user.id)
        domain = Site.objects.get_current().domain
        if domain == "example.com":
            domain = "127.0.0.1:8000"

        send_mail(email, "Verification for login attempt", f"Please click this <a href='http://{domain}/auth/verify/{v.code}'>link</a> to verify your account") # used "get base url in Django" to get back to our application for registration 

        return render(request, "authentication/registered.html")
    else:
        return render(request, "authentication/register.html")
        
def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(username=email, password=password)

        if user is not None:
            try:
                Verification.objects.get(user_id=user.id)
                return render(request, "authentication/invalid.html", {
                    "message": "Please complete your email verfication. Click <a href='/auth/verify/new'>here</a> to re-request verification"
                })
            except Verification.DoesNotExist:
                login(request, user)
            login(request, user)
            return HttpResponseRedirect("/")
        else:
            return render(request, "authentication/invalid.html", {
                "message": "Invalid credentials"
            })                 
    else:
        return render(request, "authentication/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

def verify(request, code):
    try:
        Verification.objects.get(code=code).delete()
        return HttpResponseRedirect("/auth/login/")
    except Verification.DoesNotExist:
        return render(request, "invalid.html", {
            "message": "Code is not valid or has already been used"
        })
    