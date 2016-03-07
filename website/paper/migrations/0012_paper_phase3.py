# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0011_paper_time_final'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='phase3',
            field=models.IntegerField(default=0),
        ),
    ]
