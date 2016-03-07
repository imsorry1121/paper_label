# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0012_paper_phase3'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paper',
            old_name='phase3',
            new_name='phased3',
        ),
    ]
