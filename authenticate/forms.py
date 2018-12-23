from django.shortcuts import render, get_object_or_404
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# def UserForm(request):
# name = forms.CharField(label='name',max_length=100)
# return render(request, 'polls/userForm.html', {'form': name})
# print(User._meta.get_fields())


class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password1 = forms.CharField(
        label='password1', max_length=100, widget=forms.PasswordInput)


class SignUpForm(UserCreationForm):
    # changePassword = forms.CharField(widget=forms.PasswordInput)
    # password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        password = forms.CharField(widget=forms.PasswordInput())
        fields = ['username', 'password1', 'password2', 'email']
        # widgets = {
        # 'password': forms.PasswordInput(),
        # 'changePassword': forms.PasswordInput(),
        # }
