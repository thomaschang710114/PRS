# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-16 08:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kpi', '0004_auto_20180516_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee', to=settings.AUTH_USER_MODEL),
        ),
    ]
