# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0008_auto_20160119_2150'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paper',
            old_name='labels',
            new_name='labels1',
        ),
        migrations.AddField(
            model_name='paper',
            name='labels2',
            field=models.CharField(default='', max_length=255),
        ),
    ]
