from django.urls import path, reverse_lazy
from .views import (
    CrearGrupo, ListarGrupos, UpdateGrupo, RemoveCuentaGrupo, 
    GrupoDelete
)
from django.contrib.auth.decorators import login_required
app_name = 'grupos'

urlpatterns = [
    path('crearGrupo/', login_required(CrearGrupo.as_view()), name = "crearGrupo"),
    path('listarGrupos/', login_required(ListarGrupos.as_view()), name = "listarGrupos"),
    path('modificarGrupo/<int:pk>', login_required(UpdateGrupo.as_view()), name = "modificarGrupo"),
    path('removerCuenta/<int:idCuenta>/<int:idGrupo>/<int:saldo>', login_required(RemoveCuentaGrupo.as_view()), name = "removerCuenta"),
    path('eliminarGrupo/<int:pk>', login_required(GrupoDelete.as_view()), name = "eliminarGrupo")
]