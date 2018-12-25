from django.shortcuts import render, redirect, HttpResponse, Http404
from django.contrib.auth.decorators import permission_required, login_required
from library.models import Book, BookInstance, Language, Genre, Author, User
from library.forms import BookForm, BookInstanceForm
from django.forms import modelformset_factory
from django.contrib import messages
import re


import datetime


def index(request):
    print(request.user)
    return redirect("getBooks")


def getBooks(request):
    # print(request.__dict__)
    context = {}
    print(request.user)
    # context['user'] = request.user
    context['get_books'] = (Book.objects.all())
    return render(request, "library/getBooks.html", {"context": context})


def getBook(request, pk):
    context = {}
    context['book'] = Book.objects.filter(id=pk).first()
    print(context['book'])
    return render(request, "library/getBook.html", {"context": context})


@login_required
def bookABook(request, bookId, bookInstanceId):
    book = Book.objects.get(
        id=bookId).bookinstance_set.filter(id=bookInstanceId)

    context = {

    }

    bookinstance = book[0]
    if "update" in request.path_info:
        html_url = "updateBookInstance"
    else:
        html_url = "bookABook"

    print("Inside bookABook")

    if request.method == 'POST':
        try:
            due_back = request.POST.get('due_back')
            borrower = request.POST.get('borrower')
            status = request.POST.get("status")
            print(due_back, borrower, status)
            user_bookCount = User.objects.all()[int(
                borrower)-1].bookinstance_set.all().count()
            print(user_bookCount)
            # messages.error(
            #     request, "Book Limit Count exceeded 5 this user")
            if user_bookCount < 5:
                print("dasdasdsad")

                print(borrower, due_back, status)
                (year, month, day) = re.split("/|-", due_back)
                print(year, month, day)
                due_date_converted = datetime.date(
                    year=int(year), month=int(month), day=int(day))
                if due_date_converted > datetime.date.today() + \
                        datetime.timedelta(weeks=1):
                    print("due is more reduce it")
                    messages.info(
                        request, "Due Date must be with in 1week from  today")
                elif due_date_converted < datetime.date.today():
                    print("due date must be greater than today")
                    messages.info(
                        request, "Due Date must be greater than today")

                else:

                    print(borrower)
                    bookinstance.due_back = due_date_converted
                    bookinstance.borrower_id = borrower
                    bookinstance.status = status
                    bookinstance.save()

                    messages.success(
                        request, "success")
                    return redirect("/shelf/book/"+request.path_info.split("/")[3]+"/")

                    print("Error ", e)

                    print("due date is correct")
            else:
                print("count > 5")
                messages.error(
                    request, "Book Limit Count exceeded 5 this user")
        except Exception as e:
            print("Error Exception.", e)
            return render(request, "library/"+html_url+".html", status=500)

    bookInstance = BookInstanceForm(instance=bookinstance)
    # bookInstanceFormSet = modelformset_factory(BookInstance, exclude=('id',))
    return render(request, "library/"+html_url+".html", {'context': bookInstance})


@login_required
def addBook(request):
    if request.method == 'POST':
        bookForm = BookForm(request.POST)
        if bookForm.is_valid():
            try:
                bookForm.save()
                print(request.POST['action'])
                if request.POST['action'] == 'Create':
                    print("Inside save only")
                    return redirect("../")
                else:
                    return redirect("./")
            except Exception as e:
                bookForm.error_message = e
        else:
            return Http404("Book is not saved to Database")
    else:
        bookForm = BookForm()
    return render(request, "library/createBook.html", {'context': bookForm})


@permission_required('is_staff')
def updateBook(request, pk):
    context = {
    }
    book = Book.objects.get(id=pk)
    authors = Author.objects.all()
    languages = Language.objects.all()
    genres = Genre.objects.all()

    context['book'] = book
    context['authors'] = authors
    context['genres'] = genres
    context['languages'] = languages
    if request.method == 'POST' and book is not None:
        book.title = request.POST.get('title')
        book.author_id = request.POST.get('author')
        book.language_id = request.POST.get('language')
        book.genre_id = request.POST.get('genre')
        book.save()
        return redirect("getBooks")

    return render(request, "library/updateBook.html", {'context': context})


@permission_required('is_staff')
def deleteBook(request, pk):
    # books = BookForm(request.POST)
    book = Book.objects.get(id=pk)
    book.delete()
    return redirect("getBooks")


def adminDashBoard(request):
    return render(request, "library/adminDashBoard.html")


def getBookInstances(request):
    context = {

    }
    if request.method == 'GET':
        books = Book.object.all()
        context['book'] = bookInstances


@permission_required('is_staff')
def addBookInstance(request):
    if request.method == 'POST':
        bookInstanceForm = BookInstanceForm(request.POST)
        print(bookInstanceForm)
        if bookInstanceForm.is_valid():
            bookInstanceForm.save()
        else:
            raise Http404("Book is not saved into database")

    else:
        bookInstanceForm = BookInstanceForm()

    return render(request, "library/createBook.html", {'context': bookInstanceForm})


@login_required
@permission_required('is_staff')
def updateBookInstance(request, bookId, bookInstanceId):
    a = bookABook(request, bookId, bookInstanceId)
    return a


@login_required
@permission_required('is_staff')
def deleteBookInstance(request, bookId, bookInstanceId):
    try:
        bookInstance = BookInstance.objects.get(id=bookInstanceId)
        if bookInstance:
            bookInstance.delete()
            print("Book Instance deletion success", bookInstanceId)
            return redirect("/shelf/book/" + request.path_info.split("/")[3] + "/")
        else:
            return redirect("../")

    except Exception as e:
        print("exception", e)

    return HttpResponse("library delete BookInstance")


@login_required
def returnBookInstance(request, bookId, bookInstanceId):
    book = Book.objects.get(
        id=bookId).bookinstance_set.filter(id=bookInstanceId)

    context = {

    }
    bookinstance = book[0]
    if request.method == 'POST':
        try:
            due_back = None
            borrower = None
            status = 'd'

            print(borrower, due_back, status)
            bookinstance.due_back = due_back
            bookinstance.borrower_id = borrower
            bookinstance.status = status
            bookinstance.save()

            # messages.success(
            #     request, "Book is updated with specified due date")
            return redirect("/shelf/book/"+request.path_info.split("/")[3]+"/")

            print("Error ", e)

            print("due date is correct")
        except Exception as e:
            print("Error Exception", e)
            return render(request, "library/returnBook.html", status=500)

    bookInstance = BookInstanceForm(instance=bookinstance)
    # bookInstanceFormSet = modelformset_factory(BookInstance, exclude=('id',))
    return render(request, "library/returnBook.html", {'context': bookInstance})
