# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0006_auto_20160119_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paper',
            name='author',
            field=models.CharField(max_length=500),
        ),
    ]
