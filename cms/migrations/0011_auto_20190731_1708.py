# Generated by Django 2.2.3 on 2019-07-31 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0010_auto_20190731_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='name',
            field=models.CharField(max_length=140),
        ),
    ]