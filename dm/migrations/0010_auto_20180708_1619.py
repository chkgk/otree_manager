# Generated by Django 2.0.6 on 2018-07-08 14:19

from django.db import migrations, models
import dm.models


class Migration(migrations.Migration):

    dependencies = [
        ('dm', '0009_auto_20180708_1430'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='first_login',
        ),
        migrations.AddField(
            model_name='user',
            name='public_key_set',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='public_key_file',
            field=models.FileField(upload_to=dm.models.path_and_filename),
        ),
    ]