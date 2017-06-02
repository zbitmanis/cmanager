# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Osd',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('osd_nbr', models.IntegerField()),
                ('last_active', models.DateTimeField(default=django.utils.timezone.now)),
                ('descr', models.SlugField()),
                ('status', models.SlugField()),
                ('optimisation', models.IntegerField(default=0, choices=[(0, b'Auto'), (1, b'Up'), (2, b'Down')])),
                ('optim_pct', models.IntegerField(default=-1)),
            ],
        ),
        migrations.CreateModel(
            name='OsdStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight_osd0', models.DecimalField(max_digits=6, decimal_places=5)),
                ('reweight_osd0', models.DecimalField(max_digits=6, decimal_places=5)),
                ('size_osd0', models.IntegerField()),
                ('use_osd0', models.IntegerField()),
                ('pctuse_osd0', models.DecimalField(max_digits=6, decimal_places=2)),
                ('avail_osd0', models.IntegerField()),
                ('var_osd0', models.DecimalField(max_digits=4, decimal_places=2)),
                ('pgs_osd0', models.IntegerField()),
                ('weight_osd1', models.DecimalField(max_digits=6, decimal_places=5)),
                ('reweight_osd1', models.DecimalField(max_digits=6, decimal_places=5)),
                ('size_osd1', models.IntegerField()),
                ('use_osd1', models.IntegerField()),
                ('pctuse_osd1', models.DecimalField(max_digits=6, decimal_places=2)),
                ('avail_osd1', models.IntegerField()),
                ('var_osd1', models.DecimalField(max_digits=4, decimal_places=2)),
                ('pgs_osd1', models.IntegerField()),
                ('weight_osd2', models.DecimalField(max_digits=6, decimal_places=5)),
                ('reweight_osd2', models.DecimalField(max_digits=6, decimal_places=5)),
                ('size_osd2', models.IntegerField()),
                ('use_osd2', models.IntegerField()),
                ('pctuse_osd2', models.DecimalField(max_digits=6, decimal_places=2)),
                ('avail_osd2', models.IntegerField()),
                ('var_osd2', models.DecimalField(max_digits=4, decimal_places=2)),
                ('pgs_osd2', models.IntegerField()),
                ('weight_osd3', models.DecimalField(max_digits=6, decimal_places=5)),
                ('reweight_osd3', models.DecimalField(max_digits=6, decimal_places=5)),
                ('size_osd3', models.IntegerField()),
                ('use_osd3', models.IntegerField()),
                ('pctuse_osd3', models.DecimalField(max_digits=6, decimal_places=2)),
                ('avail_osd3', models.IntegerField()),
                ('var_osd3', models.DecimalField(max_digits=4, decimal_places=2)),
                ('pgs_osd3', models.IntegerField()),
                ('weight_osd4', models.DecimalField(max_digits=6, decimal_places=5)),
                ('reweight_osd4', models.DecimalField(max_digits=6, decimal_places=5)),
                ('size_osd4', models.IntegerField()),
                ('use_osd4', models.IntegerField()),
                ('pctuse_osd4', models.DecimalField(max_digits=6, decimal_places=2)),
                ('avail_osd4', models.IntegerField()),
                ('var_osd4', models.DecimalField(max_digits=4, decimal_places=2)),
                ('pgs_osd4', models.IntegerField()),
                ('weight_osd5', models.DecimalField(max_digits=6, decimal_places=5)),
                ('reweight_osd5', models.DecimalField(max_digits=6, decimal_places=5)),
                ('size_osd5', models.IntegerField()),
                ('use_osd5', models.IntegerField()),
                ('pctuse_osd5', models.DecimalField(max_digits=6, decimal_places=2)),
                ('avail_osd5', models.IntegerField()),
                ('var_osd5', models.DecimalField(max_digits=4, decimal_places=2)),
                ('pgs_osd5', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='OsdStatsObtained',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('obtained', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='osdstats',
            name='obtained',
            field=models.ForeignKey(to='bd.OsdStatsObtained'),
        ),
    ]
