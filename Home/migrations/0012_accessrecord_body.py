# Generated by Django 3.0.5 on 2021-10-21 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0011_auto_20211021_2108'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessrecord',
            name='body',
            field=models.TextField(default=''),
        ),
    ]
