# Generated by Django 2.2.5 on 2019-11-05 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuenta', '0007_auto_20191105_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuentaPrestamo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montoNeto', models.PositiveIntegerField()),
                ('numeroPeriodoPago', models.PositiveIntegerField()),
                ('TAE', models.PositiveIntegerField()),
                ('interesNominal', models.PositiveIntegerField(blank=True, null=True)),
                ('montoInteres', models.PositiveIntegerField(blank=True, null=True)),
                ('ultimoPago', models.DateField()),
                ('cuenta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='cuenta.CuentaGenerica')),
            ],
        ),
    ]
