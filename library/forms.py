from django.forms import ModelForm
from library.models import Book, BookInstance, Author, Genre, Language


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'summary', 'genre', 'language']


class BookInstanceForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ['book', 'status']


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class GenreForm(ModelForm):
    class Meta:
        model = Genre
        fields = '__all__'


class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = '__all__'
