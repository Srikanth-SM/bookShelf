from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from authenticate.forms import LoginForm, SignInForm, Formss
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.urls import reverse_lazy
import pprint
import json
# from .models import Question, Choice

ROOT_URL = 'bookshelf/'


def home(request):
    return render(request, ROOT_URL+"home.html")


def success(request):
    session = request.user
    # print ("is user authenticated - ",request.user.is_authenticated())
    return render(request, ROOT_URL+"success.html", {"session": session})


def login(request):

    print("Inside Login")
    # check for the user if there is any logged in user
    if loginUserCheck(request):
        return render(request, "bookShelf/profile.html", {'userData': request.user})

    # if method is post then user is trying to authenticate
    else:
        if request.method == 'POST':
            # try to authenticate the user from post data
            print(request.POST)
            user = authenticate(username=request.POST['username'],
                                password=request.POST['password1'])
            print(user)
            # if there is any valid user inside django model
            if user is not None:
                # check whether that user is active and authenticated
                if user.is_active:
                    # return render(request, "success.html", {'session': user})
                    auth_login(request, user)
                    return HttpResponseRedirect("../success/")
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
    print(request.__dict__)
    print(request.user)
    return HttpResponseRedirect("../")


def signIn(request):
    # check whether to retrieve the form by using the request method
    if request.method == 'POST':
        # method is post, so trying to create a new user
        print(request.POST)
        signInForm = UserCreationForm(request.POST)
        print(signInForm)
        if signInForm.is_valid():
            signInForm.save()
            return login(request)
        else:
            print(signInForm.errors)
        return render(request, ROOT_URL+"signIn.html", {'form': signInForm})

    else:
        signInForm = UserCreationForm()

        return render(request, ROOT_URL+"signIn.html", {'form': signInForm})


def loginUserCheck(request):
    print(request.user is not None and request.user.is_authenticated)
    return request.user is not None and request.user.is_authenticated


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('../success')
    template_name = ROOT_URL+'signIn.html'
