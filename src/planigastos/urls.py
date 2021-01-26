"""planigastos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
from django.views.static import serve
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from usuario.views import Landing
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
urlpatterns = [
    path("", Landing.as_view(), name = "landing"),
    #path("/", Landing.as_view(), name = "landing"),
    path('admin/', admin.site.urls),
    path("user/", include('usuario.urls')),
    path("cuentas/", include('cuenta.urls')),
    path("transacciones/", include('transaccion.urls')),
    path("grupos/", include('Grupo.urls')),
    path("presupuesto/", include('presupuesto.urls')),
    path('accounts/reset/<uidb64>/<token>/', 
            PasswordResetConfirmView.as_view(
                template_name = "user/resetPassConfirm.html"),
            name = 'password_reset_confirm'),
    path('reset_complete', PasswordResetCompleteView.as_view(
                            template_name = "user/resetPassComplete.html"), 
        name = "password_reset_complete")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# if settings.DEBUG:
#     urlpatterns += [
#         url(r'^media/(?P<path>.*)$', serve, {
#             'document_root' : settings.MEDIA_ROOT,
#         })
#     ]