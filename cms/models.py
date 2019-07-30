from django.db import models
from django.conf import settings

from taggit.managers import TaggableManager

from .utils import *
import numpy

class Entry(models.Model):
    name = models.CharField(max_length=225)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)

    def delete(self, *args, **kwargs):
        for entry_type in (MainFile, ExtraFile):
            for object_entry in entry_type.objects.filter(entry=self):
                object_entry.delete()        
        super().delete(*args, **kwargs)

    def delete_if_exists(self, entry_type):
        if entry_type.objects.filter(entry=self).exists():
            entry_type.objects.get(entry=self).delete()

    def add_file(self, entry_type, file):
        entry_type.objects.create(entry=self, document=file).save()

    def update_entry(self, name=None, tags=None, main_file=None, extra_files=None):
        self.name = name or self.name
        if tags:
            self.tags.clear()
            for tag in tags.split(','):
                self.tags.add(tag.strip())
        if main_file:
            self.delete_if_exists(MainFile)
            self.add_file(MainFile, main_file)
        if extra_files:
            for file in extra_files:
                if file.name.endswith(".mtl"):
                    file.name = strip_ext(main_file.name) + ".obj.mtl"
                self.add_file(ExtraFile, file)
        if main_file: # we create the thumbnail last, for texture access
            create_thumbnail(MainFile.objects.get(entry=self).document.path)

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