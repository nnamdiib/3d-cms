from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('save/<int:file_id>/', views.save, name='save'),
    path('fetch/<str:file_name>/', views.get_file, name='gf'),
    path('detail/<int:stl_id>/', views.detail, name='detail'),
    path('erase/<int:file_id>/', views.erase, name='erase'),
    path('edit/<int:file_id>/', views.edit, name='edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)