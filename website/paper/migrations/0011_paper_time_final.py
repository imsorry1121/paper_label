# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0010_auto_20160131_0616'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='time_final',
            field=models.FloatField(max_length=255, default=0),
        ),
    ]
