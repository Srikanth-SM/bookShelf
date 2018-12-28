from django.conf.urls import url
from django.urls import path
from . import views


app_name = 'authenticate'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
]
