from django import forms
from .models import STLFile

class UploadForm(forms.ModelForm):

    class Meta:
        model = STLFile
        fields = ('name', 'tags', 'document')
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'id':'name'}),
            'tags': forms.TextInput(attrs={'class':'form-control', 'id':'tags'})
        }
