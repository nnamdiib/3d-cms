from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('save/<int:file_id>/', views.save, name='save'),
    path('fetch/<str:file_name>/', views.fetch, name='fetch'),
    path('fetch/<str:file_type>/<str:file_name>/', views.fetch),
    path('detail/<int:stl_id>/', views.detail, name='detail'),
    path('erase/<int:file_id>/', views.erase, name='erase'),
    path('remove_extra/<int:entry_id>/<int:extra_file_id>/', views.remove_extra, name='remove_extra'),
    path('edit/<int:entry_id>/', views.edit, name='edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)