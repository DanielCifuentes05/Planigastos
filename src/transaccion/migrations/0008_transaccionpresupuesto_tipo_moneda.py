# Generated by Django 2.2.5 on 2019-11-21 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaccion', '0007_transaccionpresupuesto'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaccionpresupuesto',
            name='tipo_moneda',
            field=models.CharField(choices=[('USD', 'USD'), ('AED', 'AED'), ('ARS', 'ARS'), ('AUD', 'AUD'), ('BGN', 'BGN'), ('BRL', 'BRL'), ('BSD', 'BSD'), ('CAD', 'CAD'), ('CHF', 'CHF'), ('CLP', 'CLP'), ('CNY', 'CNY'), ('COP', 'COP'), ('CZK', 'CZK'), ('DKK', 'DKK'), ('DOP', 'DOP'), ('EGP', 'EGP'), ('EUR', 'EUR'), ('FJD', 'FJD'), ('GBP', 'GBP'), ('GTQ', 'GTQ'), ('HKD', 'HKD'), ('HRK', 'HRK'), ('HUF', 'HUF'), ('IDR', 'IDR'), ('ILS', 'ILS'), ('INR', 'INR'), ('ISK', 'ISK'), ('JPY', 'JPY'), ('KRW', 'KRW'), ('KZT', 'KZT'), ('MXN', 'MXN'), ('MYR', 'MYR'), ('NOK', 'NOK'), ('NZD', 'NZD'), ('PAB', 'PAB'), ('PEN', 'PEN'), ('PHP', 'PHP'), ('PKR', 'PKR'), ('PLN', 'PLN'), ('PYG', 'PYG'), ('RON', 'RON'), ('RUB', 'RUB'), ('SAR', 'SAR'), ('SEK', 'SEK'), ('SGD', 'SGD'), ('THB', 'THB'), ('TRY', 'TRY'), ('TWD', 'TWD'), ('UAH', 'UAH'), ('UYU', 'UYU'), ('VND', 'VND'), ('ZAR', 'ZAR')], default='COP', max_length=3),
            preserve_default=False,
        ),
    ]
