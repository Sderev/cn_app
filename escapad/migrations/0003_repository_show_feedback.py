# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-14 15:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escapad', '0002_auto_20161213_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='show_feedback',
            field=models.BooleanField(default=False),
        ),
    ]