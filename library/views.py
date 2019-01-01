
from functools import wraps
import datetime
import re
import os
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse, Http404, render_to_response

from .models import Book, BookInstance, Language, Genre, Author, User
from .forms import BookForm, BookInstanceForm
from library.settings import AVAILABLE, MAINTAINANCE, ONLOAN, RESERVED, BOOK_LIMIT_PER_USER


BASE_TEMPLATE_DIR = 'library'


@login_required
def home(request):
    # For admin landing page is get all books.
    template = os.path.join(BASE_TEMPLATE_DIR, 'home.html')
    if request.user.is_staff:
        return redirect('get_all_books')
    else:
        context = {}
        user = request.user
        books_owned = BookInstance.objects.filter(borrower_id=user.id)
        context['books_owned'] = books_owned
        return render(request, template, context)


def get_all_books(request):
    template = os.path.join(BASE_TEMPLATE_DIR, 'get_all_books.html')
    get_books = Book.objects.all().order_by("id")
    context = {'books': get_books}
    return render(request, template, context)


@login_required
def book_detail(request, pk):
    template = os.path.join(BASE_TEMPLATE_DIR, 'book_detail.html')
    admin = request.user.is_staff
    book = Book.objects.filter(id=pk).first()
    books_owned = None
    if not admin:
        book = None
        bookinstance = BookInstance.objects.filter(
            book_id=pk, status=AVAILABLE).first()
        if user_has_this_book(request.user.id, pk):
            messages.info(request, "Cannot book Morethan one copy.")
        elif not bookinstance:
            messages.info(
                request, "There are no copies of the selected title.")
        else:
            book = bookinstance

        userid = request.user.id
        books_owned = BookInstance.get_user_books(userid)
    context = {'book': book}
    context['books_owned'] = books_owned
    return render(request, template, context)


@login_required
def rent_a_book(request, book_id, book_instance_id):
    user = request.user
    try:
        book = Book.objects.get(
            id=book_id).bookinstance_set.filter(id=book_instance_id, status=AVAILABLE).first()
        if not book:
            messages.error(
                request, "This book is not available")
            return redirect("book_detail", pk=book_id)
        context = {}
        bookinstance = book
        due_back = datetime.date.today()+datetime.timedelta(weeks=1)
        borrower = request.POST.get('borrower') or user.id
        status = ONLOAN
        user_book_count = User.objects.filter(id=int(
            borrower))[0].bookinstance_set.all().count()

        if user_book_count < BOOK_LIMIT_PER_USER:
            bookinstance.due_back = due_back
            bookinstance.borrower_id = borrower
            bookinstance.status = status
            bookinstance.save()
            messages.success(
                request, "book booked successfully")
            return redirect("home")
        else:
            messages.error(
                request, "Book Limit Count exceeded 5 for this user")
            return redirect("get_all_books")
    except Book.DoesNotExist:
        messages.error(
            request, "This book is not available")
        return redirect("book_detail", pk=book_id)


@login_required
@permission_required('is_staff')
def add_book(request):
    template = os.path.join(BASE_TEMPLATE_DIR, 'create_book.html')
    if request.method == 'POST':
        bookForm = BookForm(request.POST)
        if bookForm.is_valid():
            bookForm.save()
            if request.POST['action'] == 'Create':
                return redirect("get_all_books")
            else:
                return redirect("add_book")
        else:
            messages.warning("Form is not valid")
    book_form = BookForm()
    context = {'book_form': book_form}
    return render(request, template, context)


@login_required
@permission_required('is_staff')
def update_book(request, pk):
    template = os.path.join(BASE_TEMPLATE_DIR, 'update_book.html')
    context = {}
    try:
        book = Book.objects.get(id=pk)

        authors = Author.objects.all()
        languages = Language.objects.all()
        genres = Genre.objects.all()
        if request.method == 'POST' and book:
            book.title = request.POST.get('title')
            book.author_id = request.POST.get('author')
            book.language_id = request.POST.get('language')
            book.genre_id = request.POST.get('genre')
            book.save()
            return redirect("get_all_books")
        context = {'authors': authors, 'book': book,
                   'languages': languages, 'genres': genres}
        return render(request, template, {'context': context})
    except Book.DoesNotExist:
        return redirect("book_detail", pk=pk)


@login_required
@permission_required('is_staff')
def delete_book(request, pk):
    try:
        book = Book.objects.get(id=pk)
        if book.is_on_loan:
            messages.warning(
                "Sorry, you cannot delete the book for now as this Book copies are taken by user")
            return redirect("book_detail", pk=pk)
        book.delete()
        return redirect("get_all_books")
    except Book.DoesNotExist:
        return redirect("book_detail", pk=pk)


@login_required
@permission_required('is_staff')
def add_book_instance(request):
    template = os.path.join(BASE_TEMPLATE_DIR, 'create_book_instance.html')
    context = {}
    if request.method == 'POST':
        book_instance_form = BookInstanceForm(request.POST)
        book_id = request.POST.get('book')
        if book_instance_form.is_valid():
            instances_to_create = int(request.POST.get("instances_to_create"))
            from itertools import islice
            batch_size = 10
            objs = (BookInstance(book_id=book_id, status=AVAILABLE)
                    for i in range(instances_to_create))
            while True:
                batch = list(islice(objs, batch_size))
                if not batch:
                    break
                BookInstance.objects.bulk_create(batch, batch_size)
            messages.success(request, "book instance created successfully")
            return redirect("get_all_books")
        else:
            messages.error(request, "Book instance is not saved")
    else:
        book_instance_form = BookInstanceForm()
        context["book_instance_form"] = book_instance_form
    return render(request, template, context)


@login_required
@permission_required('is_staff')
def update_book_instance(request, book_id, book_instance_id):
    template = os.path.join(BASE_TEMPLATE_DIR, 'update_book_instance.html')
    try:
        bookinstance = Book.objects.get(id=book_id).bookinstance_set.filter(id=book_instance_id, status=AVAILABLE).first()or Book.objects.get(id=book_id).bookinstance_set.filter(id=book_instance_id,
                                                                                                                                                                                  status=MAINTAINANCE).first()
        if bookinstance:
            bookInstance = bookinstance
        else:
            bookInstance = None
            messages.error(
                request, "Cannot Perform that operation")
            return redirect("book_detail", pk=book_id)
        if request.method == 'POST':
            book = request.POST.get("book")
            status = request.POST.get('status')
            bookInstance.status = status
            bookInstance.book_id = book
            bookInstance.save()
            messages.success(
                request, "Book is Updated successfully")
            return redirect("book_detail", pk=book_id)
        instance = BookInstanceForm(instance=bookInstance)
        context = {
            'bookinstance': instance,
            'booktitle': bookinstance.book.title,
            'bookauthor': bookinstance.book.author
        }
        return render(request, template, context)

    except BookInstance.DoesNotExist:
        bookinstance = None
        return redirect("book_detail", pk=book_id)


@login_required
@permission_required('is_staff')
def delete_book_instance(request, book_id, book_instance_id):
    try:
        bookinstance = Book.objects.get(
            id=book_id).bookinstance_set.filter(id=book_instance_id, status=AVAILABLE) or Book.objects.get(
            id=book_id).bookinstance_set.filter(id=book_instance_id, status=MAINTAINANCE)
        if not bookinstance:
            bookinstance = None
            messages.error(
                request, "Cannot Perform that operation")
            return redirect("book_detail", pk=book_id)
        bookinstance.delete()
        messages.success(request, "Book is deleted successfully")
        return redirect("book_detail", pk=book_id)
    except Book.DoesNotExist:
        return render("book_detail", pk=book_id)


@login_required
def return_book(request, book_id, book_instance_id):
    try:
        book = BookInstance.objects.filter(
            id=book_instance_id, status=ONLOAN).first() or BookInstance.objects.filter(id=book_instance_id, status=RESERVED).first()

        context = {}
        bookinstance = book
        status = AVAILABLE
        bookinstance.due_back = None
        bookinstance.borrower_id = None
        bookinstance.status = status
        bookinstance.save()

        messages.success(
            request, "Book is returned successfully")
        return redirect("book_detail", pk=book_id)
    except BookInstance.DoesNotExist:
        return redirect("book_detail", pk=book_id)


def user_has_this_book(userid, pk):
    return User.objects.filter(id=userid)[
        0].bookinstance_set.filter(book_id=pk).count() >= 1
