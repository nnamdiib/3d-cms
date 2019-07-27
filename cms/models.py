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
        new_file = object.objects.create(entry=self, document=file)
        new_file.file_name = extract_file_name(new_file.document.path)
        new_file.save()

    def update_entry(self, name=None, tags=None, main_file=None, extra_files=None):
        if name:
            self.name = name
        if tags:
            self.tags.clear()
            [self.tags.add(tag.strip()) for tag in tags.split(',')]
        if main_file:
            self.add_file(MainFile, main_file)
        if extra_files:
            [self.add_file(ExtraFile, file) for file in extra_files]

class GenericFile(models.Model):
    document = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        # Whenever a file object is deleted, also delete the uploaded document
        # and the generated png thumbnail.
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
        '''
        Overriding this method because we want to create a new thumbnail
        whenever a new main file is uploaded!
        '''
        super().save(*args, **kwargs) # Calls GenericFile.save() method
        name = remove_extension(self.file_name)
        png_path = os.path.join(settings.THUMBS_ROOT, name + '.png')
        create_thumbnail(self.document.path, png_path)

class ExtraFile(GenericFile):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='extras')

    def __str__(self):
        return str(self.id)