from django.urls import path, reverse_lazy
from .views import CrearUsuario, LoginUsuario, Inicio, VerUsuario, ModificarUsuario, CambiarPass
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, 
    PasswordResetDoneView, PasswordResetConfirmView
)
from django.contrib.auth.decorators import login_required
app_name = 'usuario'

urlpatterns = [
    path('signup/', CrearUsuario.as_view(), name = "signup"),
    path('login/', LoginUsuario.as_view(), name = "login"), 
    path('logout/', LogoutView.as_view(next_page = reverse_lazy("usuario:login")), name = 'logout'),
    path('perfil/', login_required(Inicio.as_view(), login_url=reverse_lazy("usuario:login")), name = "cuentaInicio"),
    path("verPerfil/<int:pk>", login_required(VerUsuario.as_view()), name = "verPerfil"),
    path("modificar/<int:pk>", login_required(ModificarUsuario.as_view()), name = "modificar"),
    path("cambiarPass/", login_required(CambiarPass.as_view()), name = "cambiarPass"),
    path('pass_reset/',
         PasswordResetView.as_view(template_name = "user/resetPass.html", 
                                    success_url = reverse_lazy("usuario:pass_reset_done")), 
         name = 'password_reset'),
    path('pass_reset_done/', 
            PasswordResetDoneView.as_view(template_name = "user/resetPassDone.html"), 
            name = 'pass_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', 
            PasswordResetConfirmView.as_view(template_name = "user/resetPassConfirm.html"), 
            name = 'password_reset_confirm'),
]