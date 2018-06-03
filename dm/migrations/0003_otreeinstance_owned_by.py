# Generated by Django 2.0.5 on 2018-06-03 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dm', '0002_remove_otreeinstance_owned_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='otreeinstance',
            name='owned_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='dm.Experimenter'),
            preserve_default=False,
        ),
    ]
