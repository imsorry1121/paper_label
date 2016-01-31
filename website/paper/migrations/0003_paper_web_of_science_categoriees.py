# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0002_auto_20160119_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='web_of_science_categoriees',
            field=models.CharField(default='', max_length=225),
        ),
    ]
