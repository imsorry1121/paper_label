# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0009_auto_20160119_2225'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paper',
            old_name='is_choosed',
            new_name='is_phased1',
        ),
        migrations.RenameField(
            model_name='paper',
            old_name='labels1',
            new_name='label1',
        ),
        migrations.RenameField(
            model_name='paper',
            old_name='labels2',
            new_name='label2',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='is_labeled1',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='is_labeled2',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='predictions',
        ),
        migrations.AddField(
            model_name='paper',
            name='is_phased2',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='paper',
            name='label_final',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='paper',
            name='prediction',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='paper',
            name='time1',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='paper',
            name='time2',
            field=models.FloatField(default=0),
        ),
    ]
