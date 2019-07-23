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

class UpdateForm(forms.Form):
	name = forms.CharField(
		label='Upload Name',
		max_length=100,
		widget=forms.TextInput(attrs={'class':'form-control', 'id':'name'})
	)
	tags = forms.CharField(
		label='Tags',
		max_length=255,
		widget=forms.TextInput(attrs={'class':'form-control', 'id':'tags'})
	)
	document = forms.FileField()
