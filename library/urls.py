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
    path('shelf/books/', views.get_all_books, name='get_all_books'),
    path('shelf/books/<int:book_id>/take/<str:book_instance_id>/',
         views.rent_a_book, name='rent_a_book'),
    path('shelf/books/<int:pk>/update/', views.update_book, name='update_book'),
    path('shelf/books/<int:pk>/', views.book_detail, name='book_detail'),
    path('shelf/books/add/', views.add_book, name='add_book'),
    path('shelf/books/<int:pk>/delete/',
         views.delete_book, name='delete_book'),

    path('shelf/books/<int:book_id>/delete/<str:book_instance_id>/',
         views.delete_book_instance, name='delete_book_instance'),

    path('shelf/books/<int:book_id>/update/<str:book_instance_id>/',
         views.update_book_instance, name='update_book_instance'),

    path('shelf/books/<int:book_id>/return/<str:book_instance_id>/',
         views.return_book, name='return_book'),

    path('shelf/bookInstance/add/',
         views.add_book_instance, name='add_book_instance'),

    path('auth/', include('authenticate.urls'))
]
