from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Book, ReadingGoal


class SignupForm(UserCreationForm):
    """Custom signup form with email and styled fields."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label or field_name.capitalize()
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })


class BookForm(forms.ModelForm):
    """Form to add or update a book with optional PDF upload."""

    review_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Write a short review (optional)...'
        }),
        label='Your Review'
    )

    rating = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=5,
        initial=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '5'
        }),
        label='Rating (1-5)'
    )

    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'total_pages',
            'pages_read',
            'status',
            'cover_color',
            'pdf_file',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Book title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Author name'
            }),
            'total_pages': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total number of pages',
                'min': '1'
            }),
            'pages_read': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pages you have read',
                'min': '0'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cover_color': forms.TextInput(attrs={
                'class': 'form-control form-control-color',
                'type': 'color'
            }),
            'pdf_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'application/pdf,.pdf'
            }),
        }

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file and not pdf_file.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Please upload a PDF file only.')
        return pdf_file

    def clean(self):
        cleaned_data = super().clean()
        total_pages = cleaned_data.get('total_pages') or 0
        pages_read = cleaned_data.get('pages_read') or 0

        if total_pages and pages_read > total_pages:
            self.add_error('pages_read', 'Pages read cannot be greater than total pages.')

        return cleaned_data


class ReadingGoalForm(forms.ModelForm):
    """Form to update the user's reading goal."""

    class Meta:
        model = ReadingGoal
        fields = ['books_goal']
        widgets = {
            'books_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of books',
                'min': '1',
                'max': '365'
            })
        }
        labels = {
            'books_goal': 'Books Goal for this Year'
        }
