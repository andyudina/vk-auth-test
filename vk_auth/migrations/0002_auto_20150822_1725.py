# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vk_auth', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vkuser',
            old_name='acces_token',
            new_name='access_token',
        ),
    ]
