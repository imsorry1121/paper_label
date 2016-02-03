# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_user_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_phased1',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_phased2',
            field=models.BooleanField(default=False),
        ),
    ]
