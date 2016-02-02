# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20160202_0631'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='index',
            field=models.CharField(max_length=20, default=''),
        ),
    ]
