# Generated by Django 2.2.4 on 2019-11-15 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presupuesto', '0002_presupuesto_tipo_moneda'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presupuesto',
            name='saldoConsumido',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
