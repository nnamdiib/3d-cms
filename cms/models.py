from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

from .utils import *

class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entry', default=1)
    name = models.CharField(max_length=140)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)
    private = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        for entry_type in (MainFile, ExtraFile):
            for object_entry in entry_type.objects.filter(entry=self):
                object_entry.delete()        
        super().delete(*args, **kwargs)

    def get_main_file(self):
        return MainFile.objects.get(entry=self)

    def update_entry(self, name=None, tags=None, main_file=None, extra_files=None, private=None):
        self.name = name or self.name
        if tags:
            self.tags.clear()
            for tag in tags.split(','):
                self.tags.add(tag.strip())
        if main_file:
            delete_if_exists(self, MainFile)
            add_file(self, MainFile, main_file)
        if extra_files:
            for file in extra_files:
                if file.name.endswith(".obj.mtl"):
                    file.name = change_ext(main_file.name, ".obj.mtl")
                add_file(self, ExtraFile, file)
        if private:
            self.private = True
        if main_file: # we perform these last
            main_object = get_object(self, MainFile)
            main_path = main_object.document.path
            model = trimesh.load_mesh(main_path)
            create_thumbnail(main_path, model)
            x_y_z, vertices, polygons = get_metadata(model)
            main_object.vertices = vertices
            main_object.polygons = polygons
            main_object.x_axis = x_y_z[0]
            main_object.y_axis = x_y_z[1]
            main_object.z_axis = x_y_z[2]
            main_object.save()
        self.save()

class File(models.Model):
    document = models.FileField(upload_to='uploads/')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        os.remove(self.document.path)
        super().delete(*args, **kwargs)

class MainFile(File):
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE)
    vertices = models.IntegerField(null=True, default=None)
    polygons = models.IntegerField(null=True, default=None)
    x_axis = models.FloatField(null=True, default=None)
    y_axis = models.FloatField(null=True, default=None)
    z_axis = models.FloatField(null=True, default=None)

    def delete(self, *args, **kwargs):
        delete_thumbnail(self.document.path)
        super().delete(*args, **kwargs)

class ExtraFile(File):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='extra')