# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-05 12:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banner', '0007_auto_20180404_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='custom_logo',
            field=models.FileField(upload_to=b''),
        ),
        migrations.AlterField(
            model_name='event',
            name='logo',
            field=models.CharField(max_length=1000),
        ),
    ]