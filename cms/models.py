import os

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
        for f in MainFile.objects.filter(entry=self):
            f.delete()
        for ef in ExtraFile.objects.filter(entry=self):
            ef.delete()
        super().delete(*args, **kwargs)

    def add_file(self, type, file):
        new_file = type.objects.create(entry=self, document=file)
        new_file.file_name = get_file_name(new_file.document.path)
        new_file.save()

    def update_entry(self, name=None, tags=None, main_file=None, extra_files=None):
        self.name = name or self.name
        if tags:
            self.tags.clear()
            for tag in tags.split(','):
                self.tags.add(tag.strip())
        if main_file:
            MainFile.objects.filter(entry=self).update(document=file)
            self.add_file(MainFile, main_file)
        if extra_files:
            for file in extra_files:
                self.add_file(ExtraFile, file)

class File(models.Model):
    document = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        os.remove(self.document.path)
        super().delete(*args, **kwargs)

class MainFile(File):
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        create_thumbnail(self.document.path)

    def delete(self, *args, **kwargs):
        delete_thumbnail(self.document.path)
        super().delete(*args, **kwargs)

class ExtraFile(File):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='extra')