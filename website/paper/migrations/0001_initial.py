# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('isi', models.CharField(max_length=30)),
                ('author', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('journal', models.CharField(max_length=255)),
                ('year', models.CharField(max_length=10)),
                ('month', models.CharField(max_length=10)),
                ('volumn', models.CharField(max_length=10)),
                ('number', models.CharField(max_length=10)),
                ('pages', models.CharField(max_length=10)),
                ('abstract', models.TextField()),
                ('type', models.CharField(max_length=30)),
                ('keyword', models.TextField()),
                ('keywords_plus', models.TextField()),
                ('category', models.CharField(max_length=255)),
            ],
        ),
    ]
