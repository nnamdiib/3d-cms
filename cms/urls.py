from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('save/<int:file_id>/', views.save, name='save'),
    path('detail/<int:stl_id>/', views.detail, name='detail'),
    path('remove/<int:file_id>/', views.remove, name='remove'),
    path('update/<int:file_id>/', views.update, name='update')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)