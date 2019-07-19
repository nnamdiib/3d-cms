from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('download/<int:file_id>/', views.download, name='download'),
    path('detail/<int:stl_id>/', views.detail, name='detail'),
    path('delete/<int:file_id>/', views.delete, name='delete'),
]