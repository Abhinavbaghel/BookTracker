from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add-book/', views.add_book_view, name='add_book'),
    path('add-sample-books/', views.add_sample_books_view, name='add_sample_books'),
    path('read-book/<int:book_id>/', views.read_book_view, name='read_book'),
    path('delete-book/<int:book_id>/', views.delete_book_view, name='delete_book'),
    path('update-progress/<int:book_id>/', views.update_progress_view, name='update_progress'),
]
