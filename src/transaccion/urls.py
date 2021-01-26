from django.urls import path, reverse_lazy
from .views import *
from django.contrib.auth.decorators import login_required
app_name = 'transacciones'

urlpatterns = [
    path('agregarTransaccion/<int:cuenta>/', login_required(CrearTransaccion.as_view()), name = "agregarTransaccion"),
    path('listarTransacciones/<int:cuenta>/', login_required(ListarTransacciones.as_view()), name = "listarTransacciones"),
    path('listarTransaccionesO/<int:cuenta>/<str:orden>', login_required(ListarTransaccionesOrden.as_view()), name = "listarTransaccionesOrden"),
    path('eliminarTransaccion/<int:pk>/', login_required(TransaccionDelete.as_view()), name = "eliminarTransaccion"),


    path('agregarTransaccionTarjeta/<int:cuenta>/', login_required(CrearTransaccionTarjeta.as_view()), name = "agregarTransaccionTarjeta"),
    path('listarTransaccionesTarjeta/<int:cuenta>/', login_required(ListarTransaccionesTarjeta.as_view()), name = "listarTransaccionesTarjeta"),


    path('agregarTransaccionAhorros/<int:cuenta>/', login_required(CrearTransaccionAhorros.as_view()), name = "agregarTransaccionAhorros"),
    path('listarTransaccionesAhorros/<int:cuenta>/', login_required(ListarTransaccionesAhorros.as_view()), name = "listarTransaccionesAhorros"),


    path('agregarTransaccionPresupuesto/<int:cuenta>/', login_required(TransaccionPresupuestoCreate.as_view()), name = "crearTransaccionPresupuesto"),

    path('exportar/<int:pk>', login_required(exportarTransaccion), name = "exportar"),
    path('exportarPDF/<int:pk>', login_required(exportarTransaccionPDF), name = "exportarPDF")
]