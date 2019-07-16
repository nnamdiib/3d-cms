from django.db import models
from tagulous.models import TagField

class STLFile(models.Model):
    name = models.CharField(max_length=225)
    document = models.FileField(upload_to='uploads/')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    tags = TagField()
    
    def __str__(self):
        return self.name