from django.urls import path, reverse_lazy
from .views import (
    CrearPresupuesto,ListarPresupuestos, VerPresupuesto,ModificarPresupuesto,
    EliminarPresupuesto,ListarCuentaPresupuesto,ListarCuentaPresupuestoL, 
    RemoveCuentaPresupuesto
)
from django.contrib.auth.decorators import login_required
app_name = 'presupuesto'

urlpatterns = [
    path('crearPresupuesto/', login_required(CrearPresupuesto.as_view()), name = "crearPresupuesto"),
    path('listarPresupuestos/', login_required(ListarPresupuestos.as_view()), name = "listarPresupuestos"),
    path('ver/<int:pk>/', login_required(VerPresupuesto.as_view()), name = "verPresupuesto"),
    path('editar/<int:pk>/', login_required(ModificarPresupuesto.as_view()), name = "modificarPresupuesto"),
    path('eliminar/<int:pk>/', login_required(EliminarPresupuesto.as_view()), name = "eliminarPresupuesto"),
    path('transaccion/<int:pk>/', login_required(ListarCuentaPresupuesto.as_view()), name = "listarCuentaPresupuestos"),
    path('listarCuentas/<int:pk>/', login_required(ListarCuentaPresupuestoL.as_view()), name = "listarCuentaPresupuestosL"),
    path('removerCuenta/<int:idPresupuesto>/<int:idCuenta>', login_required(RemoveCuentaPresupuesto.as_view()), 
            name = "removerCuentaPresupuesto")
]