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

    def add_file(self, object, file):
        new_file = object.objects.create(entry=self, document=file)
        new_file.file_name = get_file_name(new_file.document.path)
        new_file.save()

    def update_entry(self, name=None, tags=None, main_file=None, extra_files=None):
        self.name = name or self.name
        if tags:
            self.tags.clear()
            for tag in tags.split(','):
                self.tags.add(tag.strip())
        if main_file:
            if MainFile.objects.filter(entry=self).exists():
                MainFile.objects.get(entry=self).delete()
            self.add_file(MainFile, main_file)
        if extra_files:
            for file in extra_files:
                self.add_file(ExtraFile, file)

class GenericFile(models.Model):
    document = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        # delete the uploaded file and its thumb
        name = remove_extension(self.file_name)
        png_path = os.path.join(settings.THUMBS_ROOT, name + '.png')
        delete_files(self.document.path, png_path)
        super().delete(*args, **kwargs)

    class Meta:
        abstract = True

class MainFile(GenericFile):
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # create a new thumb
        super().save(*args, **kwargs)
        name = remove_extension(self.file_name)
        png_path = os.path.join(settings.THUMBS_ROOT, name + '.png')
        create_thumbnail(self.document.path, png_path)

class ExtraFile(GenericFile):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='extras')