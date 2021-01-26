from django.db import models
from usuario.models import Usuario
from planigastos.tipoMoneda import TIPO_MONEDA
from PIL import Image
# Create your models here.

class CuentaGenerica(models.Model):
    nombre = models.CharField(max_length=100)
    icono = models.ImageField(upload_to = "cuentas/", null = True, blank = True)
    usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE, null = True, blank = True)
    tipo_moneda = models.CharField(max_length=3, choices=TIPO_MONEDA, default='COP')

    def __str__(self):
        return f'{self.nombre}'

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     img = Image.open(self.icono.path)
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.icono.path)

class CuentaEfectivo(models.Model):
    cuenta = models.OneToOneField(CuentaGenerica, on_delete = models.CASCADE)
    saldo_inicial = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.cuenta.nombre}' 

class TarjetaCredito(models.Model):
    cuenta = models.OneToOneField(CuentaGenerica, on_delete = models.CASCADE)
    pasivos = models.PositiveIntegerField()
    limite = models.PositiveIntegerField()
    cuota_manejo = models.PositiveIntegerField()
    saldo_inicial = models.PositiveIntegerField(null = True, blank = True)

    def __str__(self):
        return f'{self.cuenta.nombre}' 


class CuentaAhorros(models.Model):
    cuenta = models.OneToOneField(CuentaGenerica, on_delete = models.CASCADE)
    saldo_inicial = models.PositiveIntegerField()
    saldo_minimo_req = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.cuenta.nombre}' 


class CuentaPrestamo(models.Model):
    cuenta = models.OneToOneField(CuentaGenerica, on_delete = models.CASCADE)
    montoNeto = models.PositiveIntegerField()

    #Por simplicidad, el periodo de pago estara siempre dado en meses
    mesesPago = models.PositiveIntegerField()
    TAE = models.PositiveIntegerField()

    #Los sgtes datos se crean internamente
    interesNominal = models.PositiveIntegerField(blank = True, null = True)
    montoInteres = models.PositiveIntegerField(blank = True, null = True)
    ultimoPago = models.DateField()
    pagoMensual = models.FloatField()
    mesesPagados = models.PositiveIntegerField(default = 0)
    saldoPendiente = models.PositiveIntegerField(blank = True, null = True)

    def __str__(self):
        return f'{self.cuenta.nombre}' 