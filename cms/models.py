from django.db import models
from django.conf import settings

from taggit.managers import TaggableManager

from .utils import *

class Entry(models.Model):
    name = models.CharField(max_length=225)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)

    def delete(self, *args, **kwargs):
        for type in (MainFile, ExtraFile):
            for object in type.objects.filter(entry=self):
                object.delete()        
        super().delete(*args, **kwargs)

    def update_entry(self, name=None, tags=None, main_file=None, extra_files=None):
        self.name = name or self.name
        if tags:
            self.tags.clear()
            for tag in tags.split(','):
                self.tags.add(tag.strip()) 
        if main_file:
            updated, created = MainFile.objects.update_or_create(entry=self, defaults={"document": main_file})
            create_thumbnail(MainFile.objects.get(entry=self).document.path)
        if extra_files:
            for file in extra_files:
                ExtraFile.objects.create(entry=self, document=file)

class File(models.Model):
    document = models.FileField(upload_to='uploads/')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        delete_file(self.document.path)
        super().delete(*args, **kwargs)

class MainFile(File):
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        delete_thumbnail(self.document.path)
        super().delete(*args, **kwargs)

class ExtraFile(File):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='extra')