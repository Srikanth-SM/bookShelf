import datetime
from django.shortcuts import render, redirect, HttpResponse, Http404, render_to_response
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from library.models import Book, BookInstance, Language, Genre, Author, User
from library.forms import BookForm, BookInstanceForm
from django.forms import modelformset_factory
from django.contrib import messages
from functools import wraps
from django.http import JsonResponse
import re


def index(request):
    # # print  (request.user)
    return redirect("home")


@login_required
def home(request):
    if request.user.is_staff:
        return redirect("getBooks")
    else:
        context = {}
        try:
            userid = User.objects.filter(username=request.user)[0].id
            booksOwned = BookInstance.objects.filter(borrower_id=userid)
            context['booksOwned'] = booksOwned
            return render(request, "library/home.html", {"context": context})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=404)


def getBooks(request):
    # # print (request.__dict__)
    context = {}
    # print (request.user)
    # context['user'] = request.user
    context['get_books'] = (Book.objects.all())
    bookIds = Book.objects.order_by("id").values("id")
    avail_BookCopyCount = []
    i = 0
    for bookId in bookIds:
        print(bookId)
        a = Book.objects.filter(id=int(bookId['id']))[
            0].bookinstance_set.filter(status='a').count()
        # context['get_books'][str(bookId['id'])] = a
        avail_BookCopyCount.append(a)
        i += 1
    # context['get_books'] = (Book.objects.all())
    context['avail_BookCopyCount'] = avail_BookCopyCount
    print(context)
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
            id=bookId).bookinstance_set.filter(id=bookInstanceId, status='a')

        if book.count() < 1:
            return redirect("getBook", pk=bookId)

        context = {

        }
        userBookCopyCount = User.objects.filter(username=request.user)[
            0].bookinstance_set.filter(book_id=bookId).count()
        bookinstance = book[0]
        if "update" in request.path_info:
            html_url = "updateBookInstance"
        else:
            html_url = "bookABook"

        # if request.method == 'POST':

        due_back = datetime.date.today()+datetime.timedelta(weeks=1)
        borrower = request.POST.get('borrower') or User.objects.filter(
            username=request.user)[0].id
        status = 'o'
        # print (due_back, borrower, status)
        user_bookCount = User.objects.all()[int(
            borrower)-1].bookinstance_set.all().count()
        print("Inside bookABook")
        # print (user_bookCount)
        # messages.error(
        #     request, "Book Limit Count exceeded 5 this user")
        if user_bookCount < 5:
            # print ("dasdasdsad")

            # print (borrower, due_back, status)
            # (year, month, day) = re.split("/|-", due_back)
            # print (year, month, day)
            # due_date_converted = datetime.date(
            #     year=int(year), month=int(month), day=int(day))
            # if due_date_converted > datetime.date.today() + \
            #         datetime.timedelta(weeks=1):
                # print ("due is more reduce it")
                # messages.info(
                    # request, "Due Date must be with in 1week from  today")
            # elif due_date_converted < datetime.date.today():
                # print ("due date must be greater than today")
                # messages.info(
                    # request, "Due Date must be greater than today")

            # else:

                # print (borrower)
            bookinstance.due_back = due_back
            bookinstance.borrower_id = borrower
            bookinstance.status = status
            bookinstance.save()

            messages.success(
                request, "book booked successfully")
            return redirect("home")
            # return redirect("/shelf/book/"+request.path_info.split("/")[3]+"/")

        else:
            # print ("count > 5")
            messages.error(
                request, "Book Limit Count exceeded 5 for this user")
            return redirect("getBooks")
        # bookInstance = BookInstanceForm(instance=bookinstance)
        # bookInstanceFormSet = modelformset_factory(BookInstance, exclude=('id',))
        # return render(request, "library/" + html_url + ".html", {'context': bookInstance})
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
    # try:
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
    # except Exception as e:
    #     return JsonResponse({'message': str(e)}, status=404)


@permission_required('is_staff')
def deleteBook(request, pk):
    # books = BookForm(request.POST)
    try:
        book = Book.objects.get(id=pk)
        # do not delete the book the book copies are booked by some user.
        bookCopiesTakenByUser = (
            book.bookinstance_set.exclude(status='a')).count()
        if bookCopiesTakenByUser > 0:
            raise Exception(
                "Sorry, you cannot delete the book for now as this Book copies are taken by user")
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
            print(dir(bookInstanceForm), bookInstanceForm.data)

            # print (bookInstanceForm)
            if bookInstanceForm.is_valid():
                bookInstanceForm.save()
                return redirect("getBooks")

            else:
                raise Http404("Book is not saved into database")

        else:
            bookInstanceForm = BookInstanceForm()

        return render(request, "library/createBookInstance.html", {'context': bookInstanceForm})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)


@login_required
@permission_required('is_staff')
def updateBookInstance(request, bookId, bookInstanceId):

    try:
        bookinstance = Book.objects.get(
            id=bookId).bookinstance_set.filter(id=bookInstanceId, status='a') or Book.objects.get(
            id=bookId).bookinstance_set.filter(id=bookInstanceId, status='d')
        if bookinstance.count() > 0:
            bookInstance = bookinstance[0]
        else:
            bookInstance = None
            messages.error(
                request, "Cannot Perform that operation")
            return redirect("getBook", pk=bookId)

        print(dir(bookInstance))
        if request.method == 'POST':
            print(bookInstance)
            # due_back = request.get('due_back')
            # borrower_id = request.get('borrower') or User.objects.filter(
            #     username=request.user)[0].id
            book = request.POST.get("book")
            status = request.POST.get('status')
            # bookinstance.due_back = due_date_converted
            # bookinstance.borrower_id = borrower
            bookInstance.status = status
            bookInstance.book_id = book
            bookInstance.save()

            messages.success(
                request, "Book is Updated successfully")
            return redirect("getBook", pk=bookId)
        instance = BookInstanceForm(instance=bookInstance)
        print(instance, dir(bookinstance))
        context = {
            'bookinstance': instance,
            'booktitle': bookinstance[0].book.title,
            'bookauthor': bookinstance[0].book.author
        }
        return render(request, "library/updateBookInstance.html", {"context": context})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)


@login_required
@permission_required('is_staff')
def deleteBookInstance(request, bookId, bookInstanceId):
    try:
        bookinstance = Book.objects.get(
            id=bookId).bookinstance_set.filter(id=bookInstanceId, status='a') or Book.objects.get(
            id=bookId).bookinstance_set.filter(id=bookInstanceId, status='d')
        if bookinstance.count() > 0:
            bookinstance = bookinstance[0]
        else:
            bookinstance = None
            messages.error(
                request, "Cannot Perform that operation")
            return redirect("getBook", pk=bookId)
        if bookinstance:
            bookinstance.delete()
            messages.success(request, "Book is deleted successfully")
            # print ("Book Instance deletion success", bookInstanceId)
            return redirect("/shelf/book/" + request.path_info.split("/")[3] + "/")
        else:
            return redirect("getBook", pk=bookId)

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)


@login_required
def returnBookInstance(request, bookId, bookInstanceId):
    try:

        book = BookInstance.objects.filter(
            id=bookInstanceId, status='o') or BookInstance.objects.filter(id=bookInstanceId, status='r')
        print(book)
        if book.count() < 1:
            return redirect("getBook", pk=bookId)

        context = {

        }
        bookinstance = book[0]
        # if request.method == 'POST':

        due_back = None
        borrower = None
        status = 'd'

        # print (borrower, due_back, status)
        bookinstance.due_back = due_back
        bookinstance.borrower_id = borrower
        bookinstance.status = status
        bookinstance.save()

        messages.success(
            request, "Book is returned successfully")
        return redirect("getBook", pk=bookId)
        # bookInstance = BookInstanceForm(instance=bookinstance)
        # bookInstanceFormSet = modelformset_factory(BookInstance, exclude=('id',))
        # return render(request, "library/returnBook.html", {'context': bookInstance})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=404)
