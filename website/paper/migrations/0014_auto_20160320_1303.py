# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0013_auto_20160306_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='label3',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='paper',
            name='label4',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='paper',
            name='time3',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='paper',
            name='time4',
            field=models.FloatField(default=0),
        ),
    ]
