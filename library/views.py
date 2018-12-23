from django.shortcuts import render, redirect, HttpResponse, Http404
from django.contrib.auth.decorators import permission_required
from library.models import Book, BookInstance, Language, Genre, Author
from library.forms import BookForm, BookInstanceForm


def index(request):
    print(request.user)
    return redirect("book/")


def getBooks(request):
    # print(request.__dict__)
    context = {}
    context['user'] = request.user
    context['get_books'] = (Book.objects.all())
    return render(request, "library/getBooks.html", {"context": context})


def getBook(request, pk):
    context = Book.objects.filter(id=pk)
    return render(request, "library/getBook.html", {"context": context[0]})


@permission_required('is_staff')
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

    context['book'] = book
    context['authors'] = authors
    if request.method == 'POST' and book is not None:
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.summary = request.POST.get('summary')
        book.language = request.POST.get('language')
        book.title = request.POST.get('genre')
        print(book)
        return HttpResponse("success")

    return render(request, "library/updateBook.html", {'context': context})


@permission_required('is_staff')
def deleteBook(request, pk):
    # books = BookForm(request.POST)
    book = Book.objects.get(id=pk)
    book.delete()
    return redirect("/shelf/book/")


def adminDashBoard(request):
    return render(request, "library/adminDashBoard.html")


def getBookInstances(request):
    return HttpResponse("library get BookInstances")


@permission_required('is_staff')
def addBookInstance(request):
    if request.method == 'POST':
        bookInstanceForm = BookInstanceForm(request.POST)
        print(bookInstanceForm)
        if bookInstanceForm.is_valid() and False:
            bookInstanceForm.save()
        else:
            raise Http404("Book is not saved into database")

    else:
        bookInstanceForm = BookInstanceForm()

    return render(request, "library/createBook.html", {'context': bookInstanceForm})


def updateBookInstance(request):
    return HttpResponse("library update BookInstance")


def deleteBookInstance(request):
    return HttpResponse("library delete BookInstance")
