# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-17 15:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitload', '0002_repo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loaded_pl',
            name='id',
        ),
        migrations.RemoveField(
            model_name='loaded_pltp',
            name='id',
        ),
        migrations.RemoveField(
            model_name='repo',
            name='id',
        ),
        migrations.AlterField(
            model_name='loaded_pl',
            name='sha1',
            field=models.CharField(max_length=160, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='loaded_pltp',
            name='sha1',
            field=models.CharField(max_length=160, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='repo',
            name='name',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]