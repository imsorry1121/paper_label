# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0004_auto_20160119_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paper',
            name='volumn',
            field=models.CharField(default='', max_length=10),
        ),
    ]
