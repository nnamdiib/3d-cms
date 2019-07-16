from django import forms
from .models import STLFile


class UploadForm(forms.ModelForm):

    class Meta:
        model = STLFile
        exclude = ('date_created', 'date_updated')