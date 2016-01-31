# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='is_choosed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='paper',
            name='is_labeled1',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='paper',
            name='is_labeled2',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='paper',
            name='keyword',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='paper',
            name='keywords_plus',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='paper',
            name='type',
            field=models.CharField(default='', max_length=30),
        ),
    ]
