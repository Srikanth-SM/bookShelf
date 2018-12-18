from django.conf.urls import url
from . import views


app_name = 'authenticate'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/', views.login, name='login'),
    url(r'^success/', views.success, name='success'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^signIn/', views.signIn, name='signIn'),
    url(r'^signUp/', views.SignUp.as_view(), name='signup'),
]
