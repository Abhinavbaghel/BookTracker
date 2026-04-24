from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect

from .forms import BookForm, LoginForm, ReadingGoalForm, SignupForm
from .models import Book, ReadingGoal, Review


SAMPLE_BOOKS = [
    {
        'title': 'Focus Reading Guide',
        'author': 'BookTracker Team',
        'total_pages': 18,
        'cover_color': '#4361ee',
        'filename': 'focus-reading-guide.pdf',
    },
    {
        'title': 'Daily Learning Notes',
        'author': 'BookTracker Team',
        'total_pages': 14,
        'cover_color': '#2ec4b6',
        'filename': 'daily-learning-notes.pdf',
    },
    {
        'title': 'Mindful Study Handbook',
        'author': 'BookTracker Team',
        'total_pages': 20,
        'cover_color': '#f77f00',
        'filename': 'mindful-study-handbook.pdf',
    },
]


@csrf_protect
def signup_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            ReadingGoal.objects.create(user=user, books_goal=12, year=timezone.now().year)
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('dashboard')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = SignupForm()

    return render(request, 'tracker/signup.html', {'form': form})


@csrf_protect
def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'tracker/login.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Main dashboard showing book summary, reading stats, and timer widgets."""
    user = request.user

    reading_goal, created = ReadingGoal.objects.get_or_create(
        user=user,
        defaults={'books_goal': 12, 'year': timezone.now().year}
    )

    if request.method == 'POST' and 'update_goal' in request.POST:
        goal_form = ReadingGoalForm(request.POST, instance=reading_goal)
        if goal_form.is_valid():
            goal_form.save()
            messages.success(request, 'Reading goal updated!')
            return redirect('dashboard')
    else:
        goal_form = ReadingGoalForm(instance=reading_goal)

    all_books = Book.objects.filter(user=user)
    currently_reading = all_books.filter(status='reading')
    completed_books = all_books.filter(status='completed')
    wishlist_books = all_books.filter(status='wishlist')
    recent_reviews = Review.objects.filter(user=user).select_related('book')[:5]

    completed_count = completed_books.count()
    goal_progress = 0
    if reading_goal.books_goal > 0:
        goal_progress = round((completed_count / reading_goal.books_goal) * 100, 1)
        goal_progress = min(goal_progress, 100)

    total_pages = sum(book.total_pages for book in all_books)
    total_pages_read = sum(book.pages_read for book in all_books)
    overall_progress = 0
    if total_pages > 0:
        overall_progress = round((total_pages_read / total_pages) * 100, 1)
        overall_progress = min(overall_progress, 100)

    total_reading_minutes = sum(book.reading_minutes for book in all_books)
    pdf_books_count = all_books.exclude(pdf_file='').exclude(pdf_file__isnull=True).count()

    context = {
        'reading_goal': reading_goal,
        'goal_form': goal_form,
        'goal_progress': goal_progress,
        'currently_reading': currently_reading,
        'completed_books': completed_books,
        'wishlist_books': wishlist_books,
        'recent_reviews': recent_reviews,
        'total_books': all_books.count(),
        'completed_count': completed_count,
        'reading_count': currently_reading.count(),
        'wishlist_count': wishlist_books.count(),
        'pdf_books_count': pdf_books_count,
        'total_pages_read': total_pages_read,
        'total_pages': total_pages,
        'overall_progress': overall_progress,
        'total_reading_minutes': total_reading_minutes,
        'total_reading_hours': round(total_reading_minutes / 60, 1) if total_reading_minutes else 0,
        'sample_book_count': len(SAMPLE_BOOKS),
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def add_book_view(request):
    """Handle adding a new book with optional PDF upload."""
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user

            if book.total_pages and book.pages_read >= book.total_pages:
                book.status = 'completed'

            book.save()

            review_text = form.cleaned_data.get('review_text')
            rating = form.cleaned_data.get('rating') or 5
            if review_text:
                Review.objects.create(
                    user=request.user,
                    book=book,
                    text=review_text,
                    rating=rating
                )

            messages.success(request, f'"{book.title}" has been added to your tracker!')
            return redirect('dashboard')
        messages.error(request, 'Please fix the errors in the form.')
    else:
        form = BookForm()

    return render(request, 'tracker/add_book.html', {'form': form})


@login_required
def add_sample_books_view(request):
    """Add bundled sample PDF books to the logged-in user's library."""
    if request.method != 'POST':
        return redirect('dashboard')

    sample_dir = Path(settings.BASE_DIR) / 'sample_books'
    created_count = 0

    for sample in SAMPLE_BOOKS:
        if Book.objects.filter(user=request.user, title=sample['title']).exists():
            continue

        book = Book(
            user=request.user,
            title=sample['title'],
            author=sample['author'],
            total_pages=sample['total_pages'],
            pages_read=0,
            status='reading',
            cover_color=sample['cover_color'],
        )

        sample_path = sample_dir / sample['filename']
        if sample_path.exists():
            with open(sample_path, 'rb') as pdf_handle:
                book.pdf_file.save(sample['filename'], ContentFile(pdf_handle.read()), save=False)

        book.save()
        created_count += 1

    if created_count:
        messages.success(request, f'{created_count} sample PDF book(s) added to your library.')
    else:
        messages.info(request, 'Sample PDF books are already in your library.')

    return redirect('dashboard')


@login_required
def read_book_view(request, book_id):
    """Read a PDF book, update progress, and store reading time."""
    book = get_object_or_404(Book, id=book_id, user=request.user)

    if not book.pdf_file:
        messages.warning(request, 'This book does not have a PDF attached yet.')
        return redirect('dashboard')

    if request.method == 'POST':
        pages_read = request.POST.get('pages_read', book.pages_read)
        session_minutes = request.POST.get('session_minutes', 0)

        try:
            pages_value = max(0, min(int(pages_read), book.total_pages or 0))
            session_value = max(0, int(session_minutes or 0))

            book.pages_read = pages_value
            book.reading_minutes += session_value

            if book.total_pages and book.pages_read >= book.total_pages:
                book.status = 'completed'
            elif book.status == 'wishlist':
                book.status = 'reading'

            book.save()
            messages.success(request, f'Your progress for "{book.title}" has been saved.')
            return redirect('read_book', book_id=book.id)
        except (TypeError, ValueError):
            messages.error(request, 'Please enter valid numbers for progress and reading time.')

    return render(request, 'tracker/read_book.html', {'book': book})


@login_required
def delete_book_view(request, book_id):
    """Delete a book from the tracker."""
    book = get_object_or_404(Book, id=book_id, user=request.user)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'"{title}" has been removed from your tracker.')
    return redirect('dashboard')


@login_required
def update_progress_view(request, book_id):
    """Quickly update pages read and optionally reading minutes."""
    book = get_object_or_404(Book, id=book_id, user=request.user)
    if request.method == 'POST':
        pages_read = request.POST.get('pages_read', 0)
        session_minutes = request.POST.get('session_minutes', 0)
        try:
            book.pages_read = min(max(int(pages_read), 0), book.total_pages)
            book.reading_minutes += max(int(session_minutes or 0), 0)
            if book.total_pages and book.pages_read >= book.total_pages:
                book.status = 'completed'
            elif book.status == 'wishlist' and book.pages_read > 0:
                book.status = 'reading'
            book.save()
            messages.success(request, f'Progress updated for "{book.title}"!')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid page number.')
    return redirect('dashboard')
