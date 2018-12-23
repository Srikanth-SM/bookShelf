from django.conf.urls import url
from . import views


app_name = 'authenticate'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/', views.login, name='login'),
    url(r'^profile/', views.profile, name='profile'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^signUp/', views.signUp, name='signUp'),

    # url(r'^signUp/', views.SignUp.as_view(), name='signup'),
]
