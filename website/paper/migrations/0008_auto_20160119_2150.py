# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0007_auto_20160119_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='labels',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='paper',
            name='predictions',
            field=models.CharField(default='', max_length=255),
        ),
    ]
