# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bd', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('generation', models.IntegerField()),
                ('attempt', models.IntegerField()),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('avg', models.DecimalField(max_digits=6, decimal_places=2)),
                ('max', models.DecimalField(max_digits=6, decimal_places=2)),
                ('sum', models.DecimalField(max_digits=6, decimal_places=2)),
            ],
        ),
    ]
