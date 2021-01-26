from django.db import models
from usuario.models import Usuario
from cuenta.models import CuentaGenerica
from PIL import Image
from planigastos.tipoMoneda import TIPO_MONEDA
# Create your models here.
class Presupuesto(models.Model):
    nombre = models.CharField(max_length=100)
    duracion = models.PositiveIntegerField()
    icono = models.ImageField(upload_to="grupo/",null=True, blank=True)
    recurrencia = models.BooleanField()
    saldoTotal = models.PositiveIntegerField()

    saldoConsumido = models.IntegerField(null= True , blank= True)
    usuario = models.ForeignKey(Usuario, on_delete= models.CASCADE)
    cuentas = models.ManyToManyField(CuentaGenerica)
    
    fechaInicio = models.DateField(null = True , blank = True)
    tipo_moneda = models.CharField(choices= TIPO_MONEDA , max_length=3 , default="COP")


    def __str__(self):
        return f"{self.nombre}"

