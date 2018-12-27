"""library URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from library import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('shelf/', views.index, name='index'),
    path('shelf/home/', views.home, name='home'),
    path('shelf/dashboard', views.adminDashBoard, name='adminDashBoard'),
    path('shelf/book/', views.getBooks, name='getBooks'),
    path('shelf/book/<int:bookId>/take/<str:bookInstanceId>/',
         views.bookABook, name='bookABook'),
    path('shelf/book/<int:pk>/update/', views.updateBook, name='updateBook'),
    path('shelf/book/<int:pk>/', views.getBook, name='getBook'),
    path('shelf/book/add/', views.addBook, name='addBook'),
    path('shelf/book/<int:pk>/delete/',
         views.deleteBook, name='deleteBook'),

    path('shelf/book/<int:bookId>/delete/<str:bookInstanceId>/',
         views.deleteBookInstance, name='deleteBookInstance'),

    path('shelf/book/<int:bookId>/update/<str:bookInstanceId>/',
         views.updateBookInstance, name='updateBookInstance'),

    path('shelf/book/<int:bookId>/return/<str:bookInstanceId>/',
         views.returnBookInstance, name='returnBookInstance'),

    path('shelf/bookInstance/add/', views.addBookInstance, name='addBookInstance'),

    path('auth/', include('authenticate.urls'))
]
