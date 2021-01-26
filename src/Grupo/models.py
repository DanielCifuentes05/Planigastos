from django.db import models
from cuenta.models import CuentaGenerica
from usuario.models import Usuario
from planigastos.tipoMoneda import TIPO_MONEDA
from PIL import Image
# Create your models here.


class Grupo(models.Model):
    nombre = models.CharField(max_length = 100)
    balance = models.IntegerField(blank=True, null = True)
    cuentas = models.ManyToManyField(CuentaGenerica)
    icono = models.ImageField(upload_to = "grupos/", blank=True, null = True)
    usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE, blank = True, null = True)
    tipo_moneda = models.CharField(max_length=3, choices=TIPO_MONEDA, default='COP')

    

    def __str__(self):
        return f"{self.nombre}"