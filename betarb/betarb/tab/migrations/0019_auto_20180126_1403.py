# Generated by Django 2.0.1 on 2018-01-26 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tab', '0018_bucket_bins'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bucket',
            old_name='mean',
            new_name='error_mean',
        ),
        migrations.RenameField(
            model_name='bucket',
            old_name='std',
            new_name='error_std',
        ),
        migrations.AddField(
            model_name='bucket',
            name='total',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bucket',
            name='win_mean',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bucket',
            name='win_std',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
