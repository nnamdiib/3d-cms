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
    
    def __str__(self):
        return self.name

    def add_file(self, object, file):
        if object.objects.filter(entry=self).exists():
            object.objects.get(entry=self).delete()
        if file:
            entry = object.objects.create(entry=self, document=file)
            entry.file_name = extract_file_name(entry.document.path)
            entry.save()

    def update_entry(self, name=None, tags=None, main_file=None, extra_files=None):
        self.name = name if name
        if tags:
            self.tags.clear()
            [self.tags.add(tag.strip()) for tag in tags.split(',')]
        self.add_file(MainFile, main_file)
        [self.add_file(ExtraFile, file) for file in extra_files]

class GenericFile(models.Model):
    document = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        # Whenever an object is deleted, delete its files
        name = remove_extension(self.file_name)
        png_path = os.path.join(settings.THUMBS_ROOT, name + '.png')
        delete_files(self.document.path, png_path)
        super().delete(*args, **kwargs) # Call the real delete method

    class Meta:
        abstract = True

class MainFile(GenericFile):
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE)

    def __str__(self):
        return self.entry.name

    def save(self, *args, **kwargs):
        # Overriding this method to create a new thumbnail for every new main file
        super().save(*args, **kwargs) # Calls GenericFile.save() method
        name = remove_extension(self.file_name)
        png_path = os.path.join(settings.THUMBS_ROOT, name + '.png')
        create_thumbnail(self.document.path, png_path)

class ExtraFile(GenericFile):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='extras')

    def __str__(self):
        return str(self.id)