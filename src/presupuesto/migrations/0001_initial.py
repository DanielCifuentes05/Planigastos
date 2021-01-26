# Generated by Django 2.2.4 on 2019-11-15 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuario', '0001_initial'),
        ('cuenta', '0014_cuentagenerica_tipo_moneda'),
    ]

    operations = [
        migrations.CreateModel(
            name='Presupuesto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('duracion', models.PositiveIntegerField()),
                ('icono', models.ImageField(blank=True, null=True, upload_to='grupo/')),
                ('recurrencia', models.BooleanField()),
                ('saldoTotal', models.PositiveIntegerField()),
                ('saldoConsumido', models.PositiveIntegerField()),
                ('fechaInicio', models.DateField(blank=True, null=True)),
                ('cuentas', models.ManyToManyField(to='cuenta.CuentaGenerica')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuario.Usuario')),
            ],
        ),
    ]