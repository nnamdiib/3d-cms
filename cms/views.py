import os

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .models import Entry, MainFile, ExtraFile
from .forms import UploadForm
from .utils import *

PER_PAGE = 8

def paginate(entries, request):
    paginator = Paginator(entries, PER_PAGE)
    page = request.GET.get('p')
    request.session['page'] = page
    return paginator.get_page(page)

def register(request):
    template = 'cms/register.html'
    user_form = UserCreationForm(request.POST or None)
    # user = authenticate(request, username=username, password=password)
    if user_form.is_valid():
        user = user_form.save()
        login(request, user)
        return redirect('index')
    context = {'form': user_form}
    return render(request, template, context)

def index(request):
    template = 'cms/index.html'
    q = request.GET.get('q', None)
    if q:
        return search(request, q)    
    entries = Entry.objects.all().select_related('user').order_by('-date_created')

    uploads = paginate(entries, request)
    context = {'uploads': uploads}
    return render(request, template, context)

def search(request, q):
    template = 'cms/index.html'
    main_files = MainFile.objects.filter(
        Q(entry__name__icontains=q) | Q(entry__tags__name__icontains=q)).distinct()

    paginated_entries = paginate(main_files, request)
    context = {'uploads': paginated_entries, 'count': main_files.count(), 'q':q}
    return render(request, template, context)

def detail(request, stl_id):
    template = 'cms/detail.html'
    entry = get_object_or_404(Entry, pk=stl_id)
    if not request.user.is_superuser:
        if entry.private and entry.user != request.user:
            return Http404("You are not allowed to view this.")
    main_file = get_object_or_404(MainFile, entry=entry)
    context = {
        'entry': entry,
        'main_file': main_file,
        'extra_files': entry.extra.all(),
        'detail': True
    }
    return render(request, template, context)

@login_required
def upload(request):
    template = 'cms/upload.html'
    form = UploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        main_doc = request.FILES['main_file']
        tags = form.cleaned_data['tags']
        extra_files = request.FILES.getlist('extra_files')
        private = form.cleaned_data['private']
        entry = Entry.objects.create(name=form.cleaned_data['name'])
        entry.update_entry(tags=tags, main_file=main_doc, extra_files=extra_files, private=private)
        return HttpResponseRedirect('/')
    context = {'form': form}
    return render(request, template, context)

@login_required
def edit(request, entry_id):
    template = 'cms/upload.html'
    entry = get_object_or_404(Entry, pk=entry_id)
    if not request.user.is_superuser:
        if entry.user != request.user:
            return Http404("You are not allowed to edit this.")
    main_file = MainFile.objects.get(entry=entry)
    
    update_form = UploadForm(request.POST or None, request.FILES or None)
    update_form.fields['main_file'].required = False
    update_form.fields['extra_files'].required = False

    if update_form.is_valid():
        name = update_form.cleaned_data.get('name')
        tags = update_form.cleaned_data.get('tags')
        main_file = update_form.cleaned_data.get('main_file')
        extra_files = request.FILES.getlist('extra_files')
        private = update_form.cleaned_data.get('private')
        entry.update_entry(name, tags, main_file, extra_files, private)
        return redirect('index')

    tags = ', '.join([t.name for t in entry.tags.all()])
    init = {'name': entry.name, 'tags': tags, 'main_file': main_file.document, 'private': entry.private}
    update_form = UploadForm(initial=init)

    context = {'form': update_form, 'entry': entry, 'extra_files': entry.extra.all() }
    return render(request, template, context)

@login_required
def erase(request, file_id):
    entry = get_object_or_404(Entry, pk=file_id).delete()
    if not request.user.is_superuser:
        if entry.user != request.user:
            return Http404("You are not allowed to delete this.")
    page = request.session['page']
    if page:
        return redirect("/" + "?p=" + str(page))
    return redirect("/")

@login_required
def remove_extra(request, entry_id, extra_file_id):
    if not request.user.is_superuser:
        if entry.user != request.user:
            return Http404("You are not allowed to delete this.")
    ef = get_object_or_404(ExtraFile, pk=extra_file_id).delete()
    return redirect(reverse('edit', kwargs={'entry_id':entry_id}))

@login_required
def save(request, file_id):
    entry = Entry.objects.get(pk=file_id)
    if not request.user.is_superuser:
        if entry.private and entry.user != request.user:
            return Http404("You are not allowed to save this.")
    main_file = MainFile.objects.get(entry=entry)
    file_path = main_file.document.path
    if os.path.exists(file_path):
        return serve(request, file_path)
    raise Http404

def fetch(request, file_name):
    file_path = os.path.join(settings.UPLOADS_ROOT, file_name)
    if os.path.exists(file_path):
        return serve(request, file_path)
    raise Http404

def serve(request, file_path):
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read())
        extension = get_ext(file_path)
        response['Content-Disposition'] = 'attachment;filename=' + get_file_name(file_path)
        return response

def detail_file(request, stl_id, file_name):
    file_path = os.path.join(settings.UPLOADS_ROOT, file_name)
    if os.path.exists(file_path):
        return serve(request, file_path)
    raise Http404