from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CuentaGenerica)
admin.site.register(CuentaEfectivo)
admin.site.register(TarjetaCredito)
admin.site.register(CuentaPrestamo)
admin.site.register(CuentaAhorros)