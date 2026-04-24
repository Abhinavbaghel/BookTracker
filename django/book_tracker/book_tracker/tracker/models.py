from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ReadingGoal(models.Model):
    """Stores the user's reading goal (number of books per year)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='readinggoal')
    books_goal = models.PositiveIntegerField(default=12)
    year = models.IntegerField(default=2024)

    def __str__(self):
        return f"{self.user.username} - Goal: {self.books_goal} books in {self.year}"


class Book(models.Model):
    """Represents a book in the user's tracker, including optional PDF upload."""

    STATUS_CHOICES = [
        ('reading', 'Currently Reading'),
        ('completed', 'Completed'),
        ('wishlist', 'Wishlist'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, default='Unknown')
    total_pages = models.PositiveIntegerField(default=0)
    pages_read = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reading')
    date_added = models.DateTimeField(default=timezone.now)
    cover_color = models.CharField(max_length=7, default='#4361ee')
    pdf_file = models.FileField(upload_to='book_pdfs/', blank=True, null=True)
    reading_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def progress_percentage(self):
        """Calculate the reading progress as a percentage."""
        if self.total_pages > 0:
            percentage = (self.pages_read / self.total_pages) * 100
            return round(min(percentage, 100), 1)
        return 0

    @property
    def pages_remaining(self):
        """Calculate the number of pages remaining."""
        return max(self.total_pages - self.pages_read, 0)

    @property
    def has_pdf(self):
        return bool(self.pdf_file)


class Review(models.Model):
    """Stores short reviews written by the user for books."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"

    @property
    def star_range(self):
        """Returns range for template star rendering."""
        return range(self.rating)

    @property
    def empty_star_range(self):
        """Returns range for empty stars in template."""
        return range(5 - self.rating)
