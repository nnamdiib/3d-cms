from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='cms/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('upload/', views.upload, name='upload'),
    path('save/<int:file_id>/', views.save, name='save'),
    path('fetch/<str:file_name>/', views.fetch, name='fetch'),
    path('fetch/<str:file_type>/<str:filename>/', views.fetch),
    path('detail/<int:stl_id>/', views.detail, name='detail'),
    path('detail/<int:stl_id>/<str:file_name>', views.detail_file, name='detail_file'),
    path('erase/<int:file_id>/', views.erase, name='erase'),
    path('remove_extra/<int:entry_id>/<int:extra_file_id>/', views.remove_extra, name='remove_extra'),
    path('edit/<int:entry_id>/', views.edit, name='edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)