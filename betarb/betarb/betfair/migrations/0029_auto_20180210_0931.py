# Generated by Django 2.0.1 on 2018-02-09 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('betfair', '0028_auto_20180210_0001'),
    ]

    operations = [
        migrations.AddField(
            model_name='bet',
            name='back',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='bet',
            name='est',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bet',
            name='lay',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='bet',
            name='trade',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
