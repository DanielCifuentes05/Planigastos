# Generated by Django 2.2.5 on 2019-11-05 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuenta', '0009_auto_20191105_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuentaprestamo',
            name='mesesPagados',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
