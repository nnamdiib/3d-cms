from django.contrib import admin

from .models import STLFile

@admin.register(STLFile)
class STLFileAdmin(admin.ModelAdmin):
	list_display = ('name', 'date_created', 'date_updated')