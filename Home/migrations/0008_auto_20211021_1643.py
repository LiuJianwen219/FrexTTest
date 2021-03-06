# Generated by Django 3.0.5 on 2021-10-21 08:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0007_accessrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessrecord',
            name='access_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accessrecord',
            name='action',
            field=models.CharField(default=django.utils.timezone.now, max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accessrecord',
            name='method',
            field=models.CharField(default=django.utils.timezone.now, max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accessrecord',
            name='url_path',
            field=models.CharField(default=django.utils.timezone.now, max_length=128),
            preserve_default=False,
        ),
    ]
