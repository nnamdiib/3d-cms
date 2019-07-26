# Generated by Django 2.2.3 on 2019-07-26 20:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0006_auto_20190724_1838'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='uploads/')),
                ('file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('entry', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='cms.Entry')),
            ],
        ),
    ]
