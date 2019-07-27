import os

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, Http404
from django.urls import reverse

from .models import Entry, MainFile, ExtraFile
from .forms import UploadForm
from .utils import *

PER_PAGE = 8

def make_paginated(entries, request):
    """
    Helper function used to make a paginated list of model entries
    Used in views.index and views.search
    """
    paginator = Paginator(entries, PER_PAGE)
    page = request.GET.get('p')
    request.session['page'] = page
    return paginator.get_page(page)

def index(request):
    template = 'cms/index.html'
    q = request.GET.get('q', None)
    if q:
        return search(request, q)    
    main_files = MainFile.objects.all().select_related('entry').order_by('-date_created')

    uploads = make_paginated(main_files, request)
    context = {'uploads': uploads}
    return render(request, template, context)

def search(request, q):
    template = 'cms/index.html'
    main_files = MainFile.objects.filter(
        Q(entry__name__icontains=q) | Q(entry__tags__name__icontains=q)).distinct()

    paginated_entries = make_paginated(main_files, request)
    context = {'uploads': paginated_entries, 'count': main_files.count(), 'q':q}
    return render(request, template, context)

def upload(request):
    template = 'cms/upload.html'
    form = UploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        main_doc = request.FILES['main_file']
        tags = form.cleaned_data['tags']
        extra_files = request.FILES.getlist('extra_files')
        entry = Entry.objects.create(name=form.cleaned_data['name'])
        entry.update_entry(tags=tags, main_file=main_doc, extra_files=extra_files)
        return index(request)
    context = {'form': form}
    return render(request, template, context)

def edit(request, entry_id):
    template = 'cms/upload.html'
    entry = get_object_or_404(Entry, pk=entry_id)
    main_file = MainFile.objects.get(entry=entry)
    
    update_form = UploadForm(request.POST or None, request.FILES or None)
    update_form.fields['main_file'].required = False
    update_form.fields['extra_files'].required = False

    if update_form.is_valid():
        name = update_form.cleaned_data.get('name')
        tags = update_form.cleaned_data.get('tags')
        main_file = update_form.cleaned_data.get('main_file')
        extra_files = request.FILES.getlist('extra_files')
        entry.update_entry(name, tags, main_file, extra_files)
        return redirect('index')

    tags = ', '.join([t.name for t in entry.tags.all()])
    init = {'name': entry.name, 'tags': tags, 'main_file': main_file.document}
    update_form = UploadForm(initial=init)

    context = {'form': update_form, 'entry': entry, 'extra_files': entry.extras.all() }
    return render(request, template, context)

def save(request, file_id):
    entry = Entry.objects.get(pk=file_id)
    main_file = MainFile.objects.get(entry=entry)
    file_path = main_file.document.path
    if os.path.exists(file_path):
        return get_download(file_path, main_file.file_name)
    raise Http404

def fetch(request, file_name):
    file_path = os.path.join(settings.UPLOADS_ROOT, file_name)
    if os.path.exists(file_path):
        return get_download(file_path)
    raise Http404

def get_download(file_path):
    """
    Helper function used to prepare a file and send it
    for download in the browser client.
    Used in views.save and views.fetch
    """
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read())
        extension = get_extension(file_path)
        response['Content-Disposition'] = 'inline;'
        return response

def detail(request, stl_id):
    template = 'cms/detail.html'
    entry = get_object_or_404(Entry, pk=stl_id)
    main_file = get_object_or_404(MainFile, entry=entry)
    context = {
        'entry': entry,
        'main_file': main_file,
        'extra_files': entry.extras.all(),
        'detail': True
    }
    return render(request, template, context)

def erase(request, file_id):
    entry = get_object_or_404(Entry, pk=file_id)
    entry.delete()
    page = request.session['page']
    if page:
        return redirect("/" + "?p=" + str(page))
    return redirect("/")

def remove_extra(request, entry_id, extra_file_id):
    ef = get_object_or_404(ExtraFile, pk=extra_file_id)
    ef.delete()
    return redirect(reverse('edit', kwargs={'entry_id':entry_id}))