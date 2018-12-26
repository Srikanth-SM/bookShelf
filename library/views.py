from django.shortcuts import render, redirect, HttpResponse, Http404, render_to_response
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from library.models import Book, BookInstance, Language, Genre, Author, User
from library.forms import BookForm, BookInstanceForm
from django.forms import modelformset_factory
from django.contrib import messages
from functools import wraps
from django.http import JsonResponse
import re


import datetime


def index(request):
    # # print  (request.user)
    return redirect("getBooks")


def getBooks(request):
    # # print (request.__dict__)
    context = {}
    # print (request.user)
    # context['user'] = request.user
    context['get_books'] = (Book.objects.all())
    # context['get_books'] = (Book.objects.all())
    return render(request, "library/getBooks.html", {"context": context})


def getBook(request, pk):
    admin = request.user.is_staff
    context = {}
    try:
        if not admin:
            userBookCountCopy = User.objects.filter(username=request.user)[
                0].bookinstance_set.filter(book_id=pk).count()
            bookinstances = BookInstance.objects.filter(book_id=pk, status='a')
            if userBookCountCopy < 1 and len(bookinstances) > 0:
                context['book'] = bookinstances[0]
                # print (dir(context['book']))
            elif userBookCountCopy >= 1:
                messages.info(request, "Cannot book Morethan one copy.")
                context['book'] = None
            else:
                messages.info(request, "There are No Books of selected title.")
                context['book'] = None
            userid = User.objects.filter(username=request.user)[0].id
            booksOwned = BookInstance.objects.filter(borrower_id=userid)
            context['booksOwned'] = booksOwned

        else:
            context['book'] = Book.objects.filter(id=pk).first()
            if not context['book']:
                raise Exception("User with {0} is not present".format(pk))
            # print (context['book'])
        # print ("hai", context)
        return render(request, "library/getBook.html", {"context": context})
    except Exception as e:
        # # print (dir(e)
        kwargs = {
            'context': {'message': "hai"},
            'template_name': 'library/error.html',
            'status': 404
        }
        # return render_to_response(request, "library/error.html", {'context': str(e)})
        return JsonResponse({'message': str(e)}, status=404)


def RestrictBookCopyCountToOne(func):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        # print (args, kwargs['bookId'])
        bookId = int(kwargs['bookId'])
        userBookCopyCount = User.objects.filter(username='srikanth')[
            0].bookinstance_set.filter(book_id=kwargs['bookId']).count()
        # # print (userBookCopyCount)
        #
        if userBookCopyCount < 1:
            return func(request, *args, **kwargs)
        # return True
        return redirect("/shelf/book/")
    return wrap


@login_required
def bookABook(request, bookId, bookInstanceId):
    try:
        book = Book.objects.get(
            id=bookId).bookinstance_set.filter(id=bookInstanceId)

        context = {

        }
        userBookCopyCount = User.objects.filter(username='srikanth')[
            0].bookinstance_set.filter(book_id=bookId).count()
        if (userBookCopyCount > 1):
            raise Exception

        bookinstance = book[0]
        if "update" in request.path_info:
            html_url = "updateBookInstance"
        else:
            html_url = "bookABook"

        # print ("Inside bookABook")

        if request.method == 'POST':
            try:
                due_back = request.POST.get('due_back')
                borrower = request.POST.get('borrower') or User.objects.filter(
                    username=request.user)[0].id
                status = request.POST.get("status")
                # print (due_back, borrower, status)
                user_bookCount = User.objects.all()[int(
                    borrower)-1].bookinstance_set.all().count()
                # print (user_bookCount)
                # messages.error(
                #     request, "Book Limit Count exceeded 5 this user")
                if user_bookCount < 5:
                    # print ("dasdasdsad")

                    # print (borrower, due_back, status)
                    (year, month, day) = re.split("/|-", due_back)
                    # print (year, month, day)
                    due_date_converted = datetime.date(
                        year=int(year), month=int(month), day=int(day))
                    if due_date_converted > datetime.date.today() + \
                            datetime.timedelta(weeks=1):
                        # print ("due is more reduce it")
                        messages.info(
                            request, "Due Date must be with in 1week from  today")
                    elif due_date_converted < datetime.date.today():
                        # print ("due date must be greater than today")
                        messages.info(
                            request, "Due Date must be greater than today")

                    else:

                        # print (borrower)
                        bookinstance.due_back = due_date_converted
                        bookinstance.borrower_id = borrower
                        bookinstance.status = status
                        bookinstance.save()

                        messages.success(
                            request, "success")
                        return redirect("/shelf/book/"+request.path_info.split("/")[3]+"/")

                        # print ("Error ", e)

                        # print ("due date is correct")
                else:
                    # print ("count > 5")
                    messages.error(
                        request, "Book Limit Count exceeded 5 this user")
            except Exception as e:
                # print ("Error Exception.", e)
                return JsonResponse({'message': str(e)}, status=404)

        bookInstance = BookInstanceForm(instance=bookinstance)
        # bookInstanceFormSet = modelformset_factory(BookInstance, exclude=('id',))
        return render(request, "library/" + html_url + ".html", {'context': bookInstance})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)


@login_required
@permission_required('is_staff')
def addBook(request):
    try:
        if request.method == 'POST':
            bookForm = BookForm(request.POST)
            if bookForm.is_valid():
                try:
                    bookForm.save()
                    # print (request.POST['action'])
                    if request.POST['action'] == 'Create':
                        # print ("Inside save only")
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
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)


@permission_required('is_staff')
def updateBook(request, pk):
    try:
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
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)


@permission_required('is_staff')
def deleteBook(request, pk):
    # books = BookForm(request.POST)
    try:
        book = Book.objects.get(id=pk)
        book.delete()
        return redirect("getBooks")
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)


def adminDashBoard(request):
    return render(request, "library/adminDashBoard.html")


def getBookInstances(request):
    try:
        context = {

        }
        if request.method == 'GET':
            books = Book.object.all()
            context['book'] = bookInstances
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)


@permission_required('is_staff')
def addBookInstance(request):
    try:
        if request.method == 'POST':
            bookInstanceForm = BookInstanceForm(request.POST)
            # print (bookInstanceForm)
            if bookInstanceForm.is_valid():
                bookInstanceForm.save()
            else:
                raise Http404("Book is not saved into database")

        else:
            bookInstanceForm = BookInstanceForm()

        return render(request, "library/createBook.html", {'context': bookInstanceForm})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)


@login_required
@permission_required('is_staff')
def updateBookInstance(request, bookId, bookInstanceId):
    try:
        a = bookABook(request, bookId, bookInstanceId)
        return a
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)


@login_required
@permission_required('is_staff')
def deleteBookInstance(request, bookId, bookInstanceId):
    try:
        bookInstance = BookInstance.objects.get(id=bookInstanceId)
        # print (bookInstance.get_status_display())
        if bookInstance.get_status_display() is not 'Available':
            messages.info(
                request, "This book cannot be deleted as it is not available in library ")
        if bookInstance:
            # bookInstance.delete()
            messages.success(request, "Book is deleted successfully")
            # print ("Book Instance deletion success", bookInstanceId)
            return redirect("/shelf/book/" + request.path_info.split("/")[3] + "/")
        else:
            return redirect("../")

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)


@login_required
def returnBookInstance(request, bookId, bookInstanceId):
    try:

        book = BookInstance.objects.filter(id=bookInstanceId)

        context = {

        }
        bookinstance = book[0]
        if request.method == 'POST':
            try:
                due_back = None
                borrower = None
                status = 'd'

                # print (borrower, due_back, status)
                bookinstance.due_back = due_back
                bookinstance.borrower_id = borrower
                bookinstance.status = status
                bookinstance.save()

                # messages.success(
                #     request, "Book is updated with specified due date")
                return redirect("/shelf/book/"+request.path_info.split("/")[3]+"/")

                # print ("Error ", e)

                # print ("due date is correct")
            except Exception as e:
                # print ("Error Exception", e)
                return render(request, "library/returnBook.html", status=500)

        bookInstance = BookInstanceForm(instance=bookinstance)
        # bookInstanceFormSet = modelformset_factory(BookInstance, exclude=('id',))
        return render(request, "library/returnBook.html", {'context': bookInstance})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)
