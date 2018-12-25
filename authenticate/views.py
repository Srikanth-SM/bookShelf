from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from authenticate.forms import LoginForm, SignUpForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
import pprint
import json
# from .models import Question, Choice

ROOT_URL = 'library/'


def home(request):
    return render(request, ROOT_URL+"home.html")
    # return HttpResponse("hai")


def profile(request):
    session = request.user
    # print ("is user authenticated - ",request.user.is_authenticated()
    return HttpResponseRedirect("/shelf/")


def login(request):

    print("Inside Login")
    # check for the user if there is any logged in user
    if loginUserCheck(request):
        return HttpResponseRedirect("../profile/")

    # if method is post then user is trying to authenticate
    else:
        if request.method == 'POST':
            # try to authenticate the user from post data
            user = authenticate(username=request.POST['username'],
                                password=request.POST['password1'])
            print(user)
            # if there is any valid user inside django model
            if user is not None:
                # check whether that user is active and authenticated
                if user.is_active:
                    # return render(request, "success.html", {'session': user})
                    auth_login(request, user)
                    messages.success(request, "User logged in Successfully")
                    return HttpResponseRedirect("../profile/")
                # username is correct but password is incorrect
                else:
                    return HttpResponse("user password is correct,but user is not active")
            # simply says that username or password is incorrect
            else:
                return HttpResponse('username or password is not correct')
        # the method is GET and it will fetch the login form
        else:
            loginForm = LoginForm()
            return render(request, ROOT_URL+"index.html", {'form': loginForm})
        # return HttpResponse("hai")


def logout(request):
    auth_logout(request)
    print(request.user)
    return HttpResponseRedirect("../")


def signUp(request):
    # check whether to retrieve the form by using the request method
    if request.method == 'POST':
        # method is post, so trying to create a new user

        signUpForm = SignUpForm(request.POST)
        if signUpForm.is_valid():
            signUpForm.save()
            return login(request)
        else:
            print(signUpForm.errors)
        return render(request, ROOT_URL+"signUp.html", {'form': signUpForm})

    else:
        signUpForm = SignUpForm()

        return render(request, ROOT_URL+"signUp.html", {'form': signUpForm})


def loginUserCheck(request):
    print(request.user is not None and request.user.is_authenticated)
    return request.user is not None and request.user.is_authenticated
