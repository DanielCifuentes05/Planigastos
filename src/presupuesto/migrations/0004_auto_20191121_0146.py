# Generated by Django 2.2.5 on 2019-11-21 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presupuesto', '0003_auto_20191115_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presupuesto',
            name='saldoConsumido',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
