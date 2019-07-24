from django.contrib import admin

from .models import Entry, ExtraFile

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
	list_display = ('name', 'date_created', 'date_updated')

@admin.register(ExtraFile)
class ExtraFileAdmin(admin.ModelAdmin):
	list_display = ('entry', 'date_created', 'date_updated')