# Generated by Django 2.0.1 on 2018-01-27 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('betfair', '0002_auto_20180127_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='race_number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
