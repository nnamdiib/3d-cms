# Generated by Django 2.2.3 on 2019-07-31 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0011_auto_20190731_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainfile',
            name='dimensions',
            field=models.CharField(default=None, max_length=30, null=True),
        ),
    ]
