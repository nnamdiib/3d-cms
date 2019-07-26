# Generated by Django 2.2.3 on 2019-07-26 20:51
import os

from django.db import migrations

from cms.utils import extract_file_name


def create_main_files(apps, schema_editor):
	Entry = apps.get_model('cms', 'Entry')
	MainFile = apps.get_model('cms', 'MainFile')

	for entry in Entry.objects.all():
		main_file = MainFile.objects.create(
			entry=entry,
			document=entry.main_file,
		)
		main_file.file_name = extract_file_name(main_file.document.path)
		main_file.save()


def remove_main_files(apps, schema_editor):
	MainFile = apps.get_model('cms', 'MainFile')
	MainFile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0007_mainfile'),
    ]

    operations = [
    	migrations.RunPython(create_main_files)
    ]