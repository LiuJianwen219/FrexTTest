# Generated by Django 3.0.5 on 2021-10-21 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0010_auto_20211021_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessrecord',
            name='action',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.AddField(
            model_name='accessrecord',
            name='other_info',
            field=models.TextField(default=''),
        ),
        migrations.DeleteModel(
            name='TestRecord',
        ),
    ]