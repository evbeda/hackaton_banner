# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-14 20:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banner', '0017_auto_20180413_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='order',
            field=models.IntegerField(default=1, null=True, blank=True),
        ),
    ]
