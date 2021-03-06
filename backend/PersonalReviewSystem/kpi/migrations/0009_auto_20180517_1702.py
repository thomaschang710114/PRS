# Generated by Django 2.0.5 on 2018-05-17 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kpi', '0008_auto_20180517_1532'),
    ]

    operations = [
        migrations.CreateModel(
            name='Duration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('star_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='current_duration',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee', to='kpi.Duration'),
        ),
    ]
