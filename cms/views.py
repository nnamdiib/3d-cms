import os 
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, Http404

from .models import STLFile
from .forms import UploadForm, UpdateForm
from .utils import create_thumbnail

per_page = 8

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
        output_path = os.path.join(settings.THUMBS_ROOT, file_name + '.png')
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
    stl = STLFile.objects.get(pk=file_id)
    file_path = stl.document.path
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
    file_path = '\\\\'.join(stl.document.path.split('\\'))
    context = {'upload': upload, 'file_path': file_path, 'upload': stl}
    return render(request, template, context)

def erase(request, file_id):
    stl = get_object_or_404(STLFile, pk=file_id)
    stl_file = os.path.join(settings.BASE_DIR, stl.document.path)
    png_path = os.path.join(settings.THUMBS_ROOT, stl.file_name + '.png')
    if os.path.exists(stl_file):
        os.remove(stl_file)
    if os.path.exists(png_path):
        os.remove(png_path)
    stl.tags.clear()
    stl.delete()
    return redirect("/" + "?p=" + page)

def edit(request, file_id):
    template = 'cms/upload.html'
    stl = get_object_or_404(STLFile, pk=file_id)
    png_path = os.path.join(settings.THUMBS_ROOT, stl.file_name + '.png')

    update_form = UpdateForm(request.POST or None, request.FILES or None)
    update_form.fields['document'].required = False

    if update_form.is_valid():
        stl.name = update_form.cleaned_data['name']
        if update_form.cleaned_data['document']:
            try:
                os.remove(stl.document.path)
            except FileNotFoundError:
                print('Could not remove STL file')
            try:
                os.remove(png_path)
            except FileNotFoundError:
                print('Could not remove old PNG thumbnail')
            stl.document = update_form.cleaned_data['document']
            stl.save()  # Necessary to obtain a unique document name
            file_name = stl.document.name.split('/')[1].split('.')[0]
            stl.file_name = file_name
            stl.save()
            png_path = os.path.join(settings.THUMBS_ROOT, file_name + '.png')
            create_thumbnail(stl.document.path, png_path)
        stl.tags.clear()
        for tag in update_form.cleaned_data['tags'].split(','):
            stl.tags.add(tag.strip())
        stl.save()
        return redirect('index')

    initial_data = {
        'name': stl.name,
        'tags': ', '.join([t.name for t in stl.tags.all()]),
        'document': stl.document
    }
    update_form = UpdateForm(initial=initial_data)
    context = {'form': update_form}
    return render(request, template, context)