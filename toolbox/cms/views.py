from django.shortcuts import render

from .models import STLFile


def index(request):
	context = {}
	template = 'index.html'
	

	return render(request, template, context)
