import os

from django.db import models
from django.conf import settings

from taggit.managers import TaggableManager

from .utils import extract_file_name, create_thumbnail, delete_files

class Entry(models.Model):
    name = models.CharField(max_length=225)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)
    
    def __str__(self):
        return self.name

    def update_entry(self, name=None, tags=None, main_file=None, extra_files=None):
        if name:
            self.name = name
        if tags:
            self.tags.clear()
            [self.tags.add(tag.strip()) for tag in tags.split(',')]
        if main_file:
            try:
                old_main_file = MainFile.objects.get(entry=self).delete()
            except MainFile.DoesNotExist:
                print('No main file found')
            new_main_file = MainFile.objects.create(entry=self, document=main_file)
            new_main_file.file_name = extract_file_name(new_main_file.document.path)
            new_main_file.save()
        if extra_files:
            for file in extra_files:
                ef = ExtraFile.objects.create(entry=self, document=file)
                ef.file_name = extract_file_name(ef.document.path)
                ef.save()

class GenericFile(models.Model):
    document = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        # Whenever a file object is deleted, also delete the uploaded document
        # and the generated png thumbnail.
        name = self.remove_extension()
        png_path = os.path.join(settings.THUMBS_ROOT, name + '.png')
        delete_files(self.document.path, png_path)
        super().delete(*args, **kwargs) # Call the real delete method

    def remove_extension(self):
        '''
        Returns the file name without the extension
        example.stl --> example
        '''
        return os.path.splitext(self.file_name)[0]

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
        name = self.remove_extension()
        png_path = os.path.join(settings.THUMBS_ROOT, name + '.png')
        create_thumbnail(self.document.path, png_path)

class ExtraFile(GenericFile):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='extras')

    def __str__(self):
        return str(self.id)