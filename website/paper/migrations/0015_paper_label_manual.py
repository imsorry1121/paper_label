# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0014_auto_20160320_1303'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='label_manual',
            field=models.CharField(default='', max_length=255),
        ),
    ]
