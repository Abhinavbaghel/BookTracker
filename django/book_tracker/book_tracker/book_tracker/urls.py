from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Book Tracker'
admin.site.site_title = 'Book Tracker Admin Portal'
admin.site.index_title = 'Welcome to Book Tracker'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
