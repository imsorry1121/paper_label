# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_user_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='account',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='category',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='pwd',
            field=models.CharField(max_length=255),
        ),
    ]
