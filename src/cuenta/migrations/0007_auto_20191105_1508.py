# Generated by Django 2.2.5 on 2019-11-05 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuenta', '0006_tarjetacredito_cuota_manejo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuentaefectivo',
            name='saldo_inicial',
            field=models.PositiveIntegerField(),
        ),
    ]