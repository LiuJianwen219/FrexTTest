# Generated by Django 3.0.5 on 2021-10-09 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0005_auto_20210916_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='submitlist',
            name='ff_count',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='submitlist',
            name='lut_count',
            field=models.IntegerField(default=-1),
        ),
    ]
