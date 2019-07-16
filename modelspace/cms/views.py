from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import STLFile
from .forms import UploadForm

def index(request):
    template = 'cms/index.html'
    uploads_list = STLFile.objects.all()
    paginator = Paginator(uploads_list, 6) # 6 uploads per page
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