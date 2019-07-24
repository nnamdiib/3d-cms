from django import forms
from .models import Entry

class UploadForm(forms.Form):
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
	main_file = forms.FileField()
	extra_files = forms.FileField(
		widget=forms.ClearableFileInput(attrs={'multiple': True})
	)
