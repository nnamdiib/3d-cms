# Generated by Django 2.2.3 on 2019-07-31 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0002_mainfile_dimensions'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainfile',
            name='vertices_number',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]