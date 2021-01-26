from django.db import models
from cuenta.models import CuentaGenerica
# Create your models here.
from planigastos.tipoMoneda import TIPO_MONEDA
from presupuesto.models import Presupuesto
from PIL import Image


TIPO_TRANSACCION =  [
    (1, 'Ingreso'),
    (2, 'Gasto'),
]



class TransaccionBase(models.Model):
    cuenta = models.ForeignKey(CuentaGenerica, on_delete = models.CASCADE)
    nombre = models.CharField(max_length=100)
    tipoTransaccion = models.IntegerField(choices=TIPO_TRANSACCION, default=1)
    tipo_moneda = models.CharField(choices = TIPO_MONEDA, default = "COP", max_length=3)
    valor = models.PositiveIntegerField()
    fecha = models.DateField()
    icono = models.ImageField(upload_to = "transacciones/", blank = True, null = True )
    descripcion = models.TextField(max_length=500)



            
    def __str__(self):
        return f"{self.nombre} perteneciente a {self.cuenta.nombre} de {self.cuenta.usuario.usuariodjango}"



class TransaccionPresupuesto(models.Model):
    presupuestoOrigen = models.ForeignKey(Presupuesto, on_delete = models.CASCADE, related_name="origen")
    presupuestoDestino = models.ForeignKey(Presupuesto, on_delete = models.CASCADE, related_name="destino")
    tipo_moneda = models.CharField(choices = TIPO_MONEDA, max_length=3)
    valor = models.PositiveIntegerField()


    def __str__(self):
        return f"De {self.presupuestoOrigen.nombre} hacia {self.presupuestoDestino.nombre}"


# class ArchivosTransaccion(models.Model):
#     transaccion = models.ForeignKey(TransaccionBase, on_delete = models.CASCADE)
#     archivo = models.FileField(upload_to="exportado")


#     def __str__(self):
#         return f"Arch de {self.transaccion.nombre}"