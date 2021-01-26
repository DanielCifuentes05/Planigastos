from django.urls import path, reverse_lazy
from .views import *
from django.contrib.auth.decorators import login_required
app_name = 'cuentas'

urlpatterns = [
    path('crearEfectivo/', login_required(CuentaEfectivoCreate.as_view()), name = "crearEfectivo"),
    path('crearGenerica/', login_required(CuentaGenericaCreate.as_view()), name = "crearGenerica"),
    path('listarCuentas/', login_required(ListarCuentasEfectivo.as_view()), name = "listarCuentas"),
    path('editar/<int:pk>/', login_required(CuentaEfectivoUpdate.as_view()), name = "editarCuenta"),
    path('ver/<int:pk>/', login_required(CuentaEfectivoView.as_view()), name = "verCuenta"),
    path('eliminar/<int:pk>/', login_required(CuentaGenericaDelete.as_view()), name = "eliminarCuenta"),
    path('listarCuentasGrupo/<int:idGrupo>', login_required(ListarCuentasGrupo.as_view()), name = "listarCuentasGrupo"),

    #TARJETAS DE CREDITO
    path('listarTarjetas/', login_required(ListarTarjetas.as_view()), name = "listarTarjetas"),
    path('crearTarjeta/', login_required(TarjetaCreate.as_view()), name = "crearTarjeta"),
    path('editarTarjeta/<int:pk>/', login_required(TarjetaUpdate.as_view()), name = "editarTarjeta"),
    path('eliminarTarjeta/<int:pk>/', login_required(TarjetaDelete.as_view()), name = "eliminarTarjeta"),
    path('verTarjeta/<int:pk>', login_required(TarjetaView.as_view()), name = "verTarjeta"),


    #CUENTAS DE PRESTAMO
    path('listarPrestamo/', login_required(ListarPrestamo.as_view()), name = "listarPrestamo"),
    path('crearPrestamo/', login_required(PrestamoCreate.as_view()), name = "crearPrestamo"),
    path('eliminarPrestamo/<int:pk>/', login_required(PrestamoDelete.as_view()), name = "eliminarPrestamo"),
    path('successPrestamo/<int:pk>', login_required(SuccessPrestamoView.as_view()), name = "verPrestamo"),
    path("pagarMes/<int:pk>", login_required(pagarMesPrestamo), name = "pagarMes"),


    #CUENTAS DE AHORROS
    path('crearAhorros/', login_required(AhorrosCreate.as_view()), name = "crearAhorros"),
    path('listarAhorros/', login_required(ListarAhorros.as_view()), name = "listarAhorros"),
    path('editarAhorros/<int:pk>/', login_required(AhorrosUpdate.as_view()), name = "editarAhorros"),
    path('eliminarAhorros/<int:pk>/', login_required(AhorrosDelete.as_view()), name = "eliminarAhorros"),
    path('verAhorros/<int:pk>/', login_required(AhorrosView.as_view()), name = "verAhorros"),


    #EXPORTAR
    path('exportarCuentaCSV/<int:pk>', login_required(exportarCuentaCSV), name = "exportarCSV"),
    path('exportarCuentaPDF/<int:pk>', login_required(exportarCuentaPDF), name = "exportarPDF"),
    path('exportarPrestamo/<int:pk>', login_required(exportarPrestamoPDF), name = "exportarPrestamo")
]