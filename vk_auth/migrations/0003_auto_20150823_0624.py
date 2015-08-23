# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vk_auth', '0002_auto_20150822_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='vkuser',
            name='bdate',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vkuser',
            name='city',
            field=models.CharField(max_length=1000, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vkuser',
            name='photo',
            field=models.FilePathField(path=b'/home/nastya/vk-oauth-django/vk_oauth/images', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vkuser',
            name='sex',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='vkuser',
            name='access_token',
            field=models.CharField(max_length=4000),
        ),
    ]
