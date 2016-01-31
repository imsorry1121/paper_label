# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0003_paper_web_of_science_categoriees'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paper',
            old_name='web_of_science_categoriees',
            new_name='web_of_science_categories',
        ),
    ]
