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
from authenticate import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.landing_page),
    path('shelf/', views.home, name='home'),
    path('shelf/home/', views.home, name='home'),
    path('shelf/dashboard', views.adminDashBoard, name='adminDashBoard'),
    path('shelf/books/', views.getBooks, name='get_all_books'),
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
         views.return_book, name='return_book'),

    path('shelf/bookInstance/add/', views.addBookInstance, name='addBookInstance'),

    path('auth/', include('authenticate.urls'))
]
