from django.contrib import admin

from .models import Book, ReadingGoal, Review


@admin.register(ReadingGoal)
class ReadingGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'books_goal', 'year']
    list_filter = ['year']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'author',
        'user',
        'status',
        'pages_read',
        'total_pages',
        'progress_percentage',
        'reading_minutes',
        'date_added',
    ]
    list_filter = ['status', 'date_added']
    search_fields = ['title', 'author', 'user__username']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['book__title', 'user__username']
