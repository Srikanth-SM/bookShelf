from functools import wraps
import datetime
import re
import os

from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse, Http404, render_to_response


from .forms import BookForm, BookInstanceForm
from .models import Book, BookInstance, Language, Genre, Author, User

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
    context = {}
    book = None
    books_owned = None
    if not admin:
        user_book_count_copy = User.objects.filter(username=request.user)[
            0].bookinstance_set.filter(book_id=pk).count()
        bookinstances = BookInstance.objects.filter(book_id=pk, status='a')
        if user_book_count_copy < 1 and len(bookinstances) > 0:
            book = bookinstances[0]
        elif user_book_count_copy >= 1:
            messages.info(request, "Cannot book Morethan one copy.")
        else:
            messages.info(request, "There are No Books of selected title.")
        userid = request.user.id
        books_owned = BookInstance.get_user_books(userid)
    else:
        book = Book.objects.filter(id=pk).first()
    context['book'] = book
    context['books_owned'] = books_owned
    return render(request, template, context)


@login_required
def book_a_book(request, book_id, book_instance_id):
    userid = request.user.id
    books = Book.objects.get(
        id=book_id).bookinstance_set.filter(id=book_instance_id, status='a')

    if books.count() < 1:
        messages.error(
            request, "Book is cannot be booked as it is not available")
        return redirect("book_detail", pk=book_id)

    context = {}
    userBookCopyCount = User.objects.filter(id=userid)[
        0].bookinstance_set.filter(book_id=book_id).count()
    bookinstance = books[0]
    due_back = datetime.date.today()+datetime.timedelta(weeks=1)
    borrower = request.POST.get('borrower') or request.user.id
    status = 'o'
    user_book_count = User.objects.filter(id=int(
        borrower))[0].bookinstance_set.all().count()

    if user_book_count < 5:
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


@login_required
@permission_required('is_staff')
def add_book(request):
    template = os.path.join(BASE_TEMPLATE_DIR, 'createBook.html')
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
    bookForm = BookForm()
    context = {'bookForm': bookForm}
    return render(request, template, context)


@login_required
@permission_required('is_staff')
def update_book(request, pk):
    template = os.path.join(BASE_TEMPLATE_DIR, 'updateBook.html')
    context = {}
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


@login_required
@permission_required('is_staff')
def delete_book(request, pk):
    book = Book.objects.get(id=pk)
    book_copies_taken_by_user = (
        book.bookinstance_set.exclude(status='a')).count()
    if book_copies_taken_by_user > 0:
        messages.warning(
            "Sorry, you cannot delete the book for now as this Book copies are taken by user")
        return redirect("book_detail", pk=pk)
    book.delete()
    return redirect("get_all_books")


def adimin_dashboard(request):
    return render(request, "library/adminDashBoard.html")


@login_required
@permission_required('is_staff')
def add_book_instance(request):
    template = os.path.join(BASE_TEMPLATE_DIR, 'createBookInstance.html')
    context = {}
    if request.method == 'POST':
        bookInstanceForm = BookInstanceForm(request.POST)
        if bookInstanceForm.is_valid():
            bookInstanceForm.save()
            messages.success(request, "book instance created successfully")
            return redirect("get_all_books")
        else:
            messages.error(request, "Book instance is not saved")
    else:
        bookInstanceForm = BookInstanceForm()
        context["bookInstanceForm"] = bookInstanceForm
    return render(request, template, context)


@login_required
@permission_required('is_staff')
def update_book_instance(request, book_id, book_instance_id):
    template = os.path.join(BASE_TEMPLATE_DIR, 'updateBookInstance.html')
    bookinstance = Book.objects.get(
        id=book_id).bookinstance_set.filter(id=book_instance_id, status='a') or Book.objects.get(
        id=book_id).bookinstance_set.filter(id=book_instance_id, status='d')
    if bookinstance.count() > 0:
        bookInstance = bookinstance[0]
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
        'booktitle': bookinstance[0].book.title,
        'bookauthor': bookinstance[0].book.author
    }
    return render(request, template, context)


@login_required
@permission_required('is_staff')
def delete_book_instance(request, book_id, book_instance_id):
    bookinstance = Book.objects.get(
        id=book_id).bookinstance_set.filter(id=book_instance_id, status='a') or Book.objects.get(
        id=book_id).bookinstance_set.filter(id=book_instance_id, status='d')
    if bookinstance.count() > 0:
        bookinstance = bookinstance[0]
    else:
        bookinstance = None
        messages.error(
            request, "Cannot Perform that operation")
        return redirect("book_detail", pk=book_id)
    bookinstance.delete()
    messages.success(request, "Book is deleted successfully")
    return redirect("book_detail", pk=book_id)


@login_required
def return_book(request, book_id, book_instance_id):
    book = BookInstance.objects.filter(
        id=book_instance_id, status='o') or BookInstance.objects.filter(id=book_instance_id, status='r')
    if book.count() < 1:
        return redirect("book_detail", pk=book_id)
    context = {}
    bookinstance = book[0]
    due_back = None
    borrower = None
    status = 'a'
    bookinstance.due_back = due_back
    bookinstance.borrower_id = borrower
    bookinstance.status = status
    bookinstance.save()

    messages.success(
        request, "Book is returned successfully")
    return redirect("book_detail", pk=book_id)
    # bookInstance = BookInstanceForm(instance=bookinstance)
    # bookInstanceFormSet = modelformset_factory(BookInstance, exclude=('id',))
    # return render(request, "library/returnBook.html", {'context': bookInstance})
