# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0005_auto_20160119_1431'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paper',
            old_name='volumn',
            new_name='volume',
        ),
    ]
