# -*- coding: utf-8 -*-
# Generated by Django 1.11rc1 on 2017-04-06 14:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField(blank=True, max_length=100)),
                ('lon', models.FloatField(blank=True, max_length=100)),
                ('name', models.CharField(max_length=250)),
                ('surname', models.CharField(max_length=250)),
                ('chat_id', models.CharField(max_length=250)),
                ('lastCommand', models.CharField(blank=True, max_length=1000)),
            ],
        ),
    ]
