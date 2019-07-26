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
from .utils import create_thumbnail, extract_file_name

PER_PAGE = 8

def make_paginated_entries(entries, request):
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
    
    entries = MainFile.objects.all().select_related('entry').order_by('-date_created')

    uploads = make_paginated_entries(entries, request)
    context = {'uploads': uploads}
    return render(request, template, context)

def search(request, q):
    template = 'cms/index.html'
    entries = Entry.objects.filter(
        Q(name__icontains=q) | Q(tags__name__icontains=q)).distinct()

    paginated_entries = make_paginated_entries(entries, request)
    context = {'uploads': paginated_entries, 'count': entries.count(), 'q':q}
    return render(request, template, context)

def upload(request):
    template = 'cms/upload.html'
    form = UploadForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        main_doc = request.FILES['main_file']
        tags = form.cleaned_data['tags']
        extra_files = request.FILES.getlist('extra_files')

        entry = Entry.objects.create(name=form.cleaned_data['name'])
        main_file = MainFile.objects.create(entry=entry, document=main_doc)

        if tags:
            [entry.tags.add(tag.strip()) for tag in tags.split(',')]
        entry.save()

        for file in extra_files:
            ef = ExtraFile.objects.create(entry=entry, document=file)
            ef.file_name = ef.get_name_with_extension()
            ef.save()

        name = main_file.file_name.split('.')[0]
        output_path = os.path.join(settings.THUMBS_ROOT, name + '.png')
        create_thumbnail(main_file.document.path, output_path)
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
        extra_files = request.FILES.getlist('extra_files')
        entry.name = update_form.cleaned_data['name']
        entry.save()
        # Handle a new main file
        if update_form.cleaned_data['main_file']:
            old_doc_path = main_file.document.path
            name =  main_file.file_name.split('.')[0]
            old_png_path = os.path.join(settings.THUMBS_ROOT, name + '.png')
            
            main_file.document = update_form.cleaned_data['main_file']
            main_file.save()

            try:
                os.remove(old_doc_path)
                os.remove(old_png_path)
            except FileNotFoundError:
                print('Error while attempting to delete file(s).')

            name = main_file.file_name.split('.')[0]
            png_path = os.path.join(settings.THUMBS_ROOT, name + '.png')
            create_thumbnail(main_file.document.path, png_path)

        # Handle (any) new tags
        entry.tags.clear()
        tags = update_form.cleaned_data['tags']
        if tags:
            [entry.tags.add(tag.strip()) for tag in tags.split(',')]
        entry.save()

        # Handle (any) new extra files
        if extra_files:
            for file in extra_files:
                ef = ExtraFile.objects.create(
                    entry=entry,
                    document=file
                )
                ef.file_name = extract_file_name(ef.document.path)
                ef.save()

        return redirect('index')

    initial_data = {
        'name': entry.name,
        'tags': ', '.join([t.name for t in entry.tags.all()]),
        'main_file': main_file.document,
    }

    update_form = UploadForm(initial=initial_data)
    update_form.fields['main_file'].required = False
    update_form.fields['extra_files'].required = False

    context = {
        'form': update_form,
        'entry': entry,
        'extra_files': entry.extras.all()
    }
    return render(request, template, context)

def save(request, file_id):
    entry = Entry.objects.get(pk=file_id)
    mf = MainFile.objects.get(entry=entry)
    file_path = main_file.document.path
    if os.path.exists(file_path):
        return get_download(file_path, main_file.file_name)
    raise Http404

def fetch(request, file_name, file_type=None):
    if file_type == 'extra':
        ef = get_object_or_404(ExtraFile, file_name=file_name)
        file_path = ef.document.path
    else:
        main_file = get_object_or_404(MainFile, file_name=file_name)
        file_path = main_file.document.path
    if os.path.exists(file_path):
        return get_download(file_path, file_name)
    raise Http404

def get_download(file_path, name):
    """
    Helper function used to prepare a .stl file and send it
    for download in the browser client.
    Used in views.save and views.fetch
    """
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read())
        extension = os.path.splitext(file_path)[-1]
        response['Content-Disposition'] = 'inline; filename=' + name + extension
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
    stl = get_object_or_404(Entry, pk=file_id)
    main_file = get_object_or_404(MainFile, entry=stl)
    thumb_name = main_file.file_name.split('.')[0] + '.png'
    stl_file = os.path.join(settings.BASE_DIR, main_file.document.path)
    png_path = os.path.join(settings.THUMBS_ROOT, thumb_name)
    try:
        os.remove(stl_file)
        os.remove(png_path)
    except FileNotFoundError:
        print("File(s) not found.")
    stl.tags.clear()
    stl.delete()
    page = request.session['page']
    if page:
        return redirect("/" + "?p=" + str(page))
    return redirect("/")

def remove_extra(request, entry_id, extra_file_id):
    ef = get_object_or_404(ExtraFile, pk=extra_file_id)
    ef.delete()
    return redirect(reverse('edit', kwargs={'entry_id':entry_id}))