# Generated by Django 2.2.5 on 2019-10-30 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cuenta', '0003_auto_20191007_1657'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('balance', models.IntegerField()),
                ('cuentas', models.ManyToManyField(to='cuenta.CuentaGenerica')),
            ],
        ),
    ]
