# Generated by Django 2.0.1 on 2018-02-04 06:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('betfair', '0021_auto_20180201_1757'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_type', models.CharField(max_length=50)),
                ('price', models.FloatField()),
                ('size', models.FloatField()),
                ('side', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=30)),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='betfair.Market')),
                ('runner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='betfair.Runner')),
            ],
        ),
    ]
