# python built-in packages
import json
import os
import pprint

# 3rd party packages
from authenticate.forms import LoginForm, SignUpForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

# application level imports

BASE_TEMPLATE_DIR = 'auth'


def landing_page(request):
    template = os.path.join(BASE_TEMPLATE_DIR, 'index.html')
    return render(request, template)


def login(request):
    template = os.path.join(BASE_TEMPLATE_DIR, 'login.html')

    if is_user_authenticated(request):
        return redirect(reverse('home'))

    if request.method == 'POST':
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password1'])

        if user:
            if user.is_active:
                auth_login(request, user)
                messages.success(request, "User logged in Successfully")
                return redirect(reverse('home'))
            else:
                return HttpResponse("user is not active")
        else:
            return HttpResponse('username or password is not correct')
    else:
        loginForm = LoginForm()
        return render(request, template, {'form': loginForm})


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")


def signup(request):
    template = os.path.join(BASE_TEMPLATE_DIR, 'signup.html')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('authenticate:login'))

        context = {'form': form}
        return render(request, template, context)
    else:
        form = SignUpForm()
        context = {'form': form}

        return render(request, template, context)


def is_user_authenticated(request):
    return request.user is not None and request.user.is_authenticated
