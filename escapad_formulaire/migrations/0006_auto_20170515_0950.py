# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-15 09:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('escapad_formulaire', '0005_auto_20170512_0912'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cours',
            name='url_media',
        ),
        migrations.RemoveField(
            model_name='module',
            name='url_media',
        ),
    ]