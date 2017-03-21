# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-08 16:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Azure_Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vmail', models.CharField(max_length=50)),
                ('vpass', models.CharField(max_length=50)),
                ('vsubid', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('mail', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=20)),
                ('azure_acc', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='newapp.Azure_Account')),
            ],
        ),
    ]
