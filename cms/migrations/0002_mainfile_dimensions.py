# Generated by Django 2.2.3 on 2019-07-30 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainfile',
            name='dimensions',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
    ]
