import os 
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, Http404

from .models import STLFile
from .forms import UploadForm
from .utils import create_thumbnail

per_page = 20

def index(request):
    q = request.GET.get('q', None)
    if q:
        return search(request, q)
    template = 'cms/index.html'
    entries = STLFile.objects.all().order_by('-date_created')

    paginator = Paginator(entries, per_page)
    page = request.GET.get('p')
    uploads = paginator.get_page(page)

    context = {'uploads': uploads}
    return render(request, template, context)

def upload(request):
    template = 'cms/upload.html'
    form = UploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        entry = form.save()
        stl_path = entry.document.path
        file_name = entry.document.name.split('/')[1].split('.')[0]
        folder = os.path.join(os.path.join(settings.STATIC_ROOT, 'img'), 'thumbs')
        output_path = os.path.join(folder, file_name + '.png')
        create_thumbnail(stl_path, output_path)
        entry.file_name = file_name
        entry.save()
        return redirect('/')
    context = {'form': form}
    return render(request, template, context)

def search(request, q):
    template = 'cms/index.html'
    entries = STLFile.objects.filter(Q(name__icontains=q) | Q(tags__name__icontains=q)).distinct()

    paginator = Paginator(entries, per_page)
    page = request.GET.get('p')
    uploads = paginator.get_page(page)

    context = {'uploads': uploads, 'count': entries.count(), 'q':q}
    return render(request, template, context)

def save(request, file_id):
    stl = STLFile.objects.get(pk=file_id) # get_object_or_404(STLFile, pk=file_id)
    file_path = os.path.join(settings.BASE_DIR, stl.document.path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="model/stl")
            extension = os.path.splitext(file_path)[-1]
            response['Content-Disposition'] = 'inline; filename=' + stl.name + extension
            return response
    raise Http404

def detail(request, stl_id):
    template = 'cms/detail.html'
    stl = get_object_or_404(STLFile, pk=stl_id)
    file_path = os.path.join(settings.BASE_DIR, stl.document.path)
    file_path = '\\\\'.join(file_path.split('\\'))
    context = {'upload': upload, 'file_path': file_path, 'upload': stl}
    return render(request, template, context)

def remove(request, file_id):
    entries = STLFile.objects.all()
    stl = get_object_or_404(STLFile, pk=file_id)
    stl_file = os.path.join(settings.BASE_DIR, stl.document.path)
    folder = os.path.join(os.path.join(settings.STATIC_ROOT, 'img'), 'thumbs')
    png_path = os.path.join(folder, stl.file_name + '.png')
    if os.path.exists(stl_file):
        os.remove(stl_file)
    if os.path.exists(png_path):
        os.remove(png_path)
    stl.tags.clear()
    stl.delete()
    count = len(entries)
    page = (count - 1) / per_page
    if page < 1:
        return redirect("/")
    return redirect("/" + "?p=" + page)