import os 
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, Http404

from .models import STLFile
from .forms import UploadForm

per_page = 20

def index(request):
    q = request.GET.get('q', None)
    if q:
        return search(request, q)
    template = 'cms/index.html'
    uploads_list = STLFile.objects.all().order_by('-date_created')

    paginator = Paginator(uploads_list, per_page)
    page = request.GET.get('p')
    request.session['count'] = len(uploads_list)
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
        return redirect('/')
    context = {'form': form}
    return render(request, template, context)

def search(request, q):
    template = 'cms/search_results.html'
    search_results = STLFile.objects.filter(Q(name__icontains=q) | Q(tags__name__icontains=q)).distinct()

    paginator = Paginator(search_results, per_page)
    page = request.GET.get('p')
    request.session['count'] = len(search_results)
    uploads = paginator.get_page(page)

    context = {'uploads': uploads, 'count': search_results.count(), 'q':q}
    return render(request, template, context)

def download(request, file_id):
    stl = STLFile.objects.get(pk=file_id) # get_object_or_404(STLFile, pk=file_id)
    file_path = os.path.join(settings.BASE_DIR, stl.document.path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="model/stl")
            extension = os.path.splitext(file_path)[-1]
            response['Content-Disposition'] = 'inline; filename=' + stl.name + extension
            return response
    raise Http404

def delete(request, file_id):
    stl = STLFile.objects.get(pk=file_id).delete()
    count = request.session['count']
    page = (count - 1) / per_page
    if page is None or page >= 1:
        return redirect("/")
    return redirect("/" + "?p=" + page)