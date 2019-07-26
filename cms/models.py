from django.db import models
from taggit.managers import TaggableManager

from .utils import extract_file_name


class Entry(models.Model):
    name = models.CharField(max_length=225)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)
    
    def __str__(self):
        return self.name

    def get_name_without_extension(self):
        return self.main_file.name.split('/')[1].split('.')[0]

    def get_name_with_extension(self):
        return self.main_file.name.split('/')[1]

# To Do, create  GenericFile superclass for MainFile and EntryFile
class MainFile(models.Model):
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE)
    document = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.entry.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # Call the real save method
        self.file_name = extract_file_name(self.document.path)
        super().save(*args, **kwargs) # Call the real save method

    def remove_extension(self):
        return self.file_name.split('.')[0]


class ExtraFile(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='extras')
    document = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    def get_name_without_extension(self):
        return self.document.name.split('/')[1].split('.')[0]

    def get_name_with_extension(self):
        return self.document.name.split('/')[1]