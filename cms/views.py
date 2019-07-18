from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import STLFile
from .forms import UploadForm

def index(request):
    q = request.GET.get('q', None)
    if q:
        return search(request, q)
    template = 'cms/index.html'
    uploads_list = STLFile.objects.all()

    paginator = Paginator(uploads_list, 8) # 6 uploads per page
    page = request.GET.get('page')
    uploads = paginator.get_page(page)

    context = {'uploads': uploads}
    return render(request, template, context)

def upload(request):
    template = 'cms/upload.html'
    form = UploadForm(request.POST or None, request.FILES or None)
    print(request.POST)
    if form.is_valid():
        print('VALID *******')
        print(form.cleaned_data)
        form.save()
        return index(request)

    context = {'form': form}
    return render(request, template, context)

def search(request, q):
    template = 'cms/search_results.html'
    search_results = STLFile.objects.filter(Q(name__icontains=q) | Q(tags__name__icontains=q)).distinct()

    paginator = Paginator(search_results, 8) # 6 uploads per page
    page = request.GET.get('page')
    uploads = paginator.get_page(page)

    context = {'uploads': uploads, 'count': search_results.count(), 'q':q}
    return render(request, template, context)