# Generated by Django 3.0.5 on 2021-10-29 04:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Simulate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulaterecord',
            name='code',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]