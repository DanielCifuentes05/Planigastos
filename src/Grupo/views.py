from django.shortcuts import render, get_object_or_404
from .models import Grupo
from .forms import CrearGrupoForm, CrearGrupoForm2
from django.views import View
from django.views.generic import (
    CreateView, ListView, UpdateView, TemplateView, 
    DeleteView
)
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from usuario.models import Usuario
from django.http import HttpResponseRedirect
from cuenta.models import CuentaGenerica
from planigastos.convertirMoneda import cambiarMoneda
# Create your views here.


class CrearGrupo(CreateView):
    template_name = "grupos/crearGrupo.html"
    model = Grupo
    form_class = CrearGrupoForm
    success_url = reverse_lazy("grupos:listarGrupos")

    def get_form_kwargs(self):
        kwargs = super(CrearGrupo, self).get_form_kwargs()
        kwargs.update({'usuario': self.request.user})
        return kwargs


class ListarGrupos(ListView):
    model = Grupo
    template_name = 'grupos/listarGrupos.html'
    paginate_by = 4


    def get_queryset(self):
        usuario = (Usuario.objects.get(usuariodjango = self.request.user))
        return Grupo.objects.filter(usuario = usuario).order_by('-id')


class UpdateGrupo(UpdateView):
    template_name = "grupos/modificarGrupos.html"
    model = Grupo
    form_class = CrearGrupoForm2
    success_url = reverse_lazy("grupos:cuentaInicio")

    def get_success_url(self):
        return reverse_lazy('cuentas:listarCuentasGrupo', kwargs = {'idGrupo' : self.kwargs['pk'] })

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Grupo, id = id_)


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateGrupo, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateGrupo, self).get_form_kwargs()
        kwargs.update({'usuario': self.request.user, 'grupo' : self.kwargs['pk']})
        return kwargs



class RemoveCuentaGrupo(TemplateView):
    model = Grupo
    template_name = "grupos/removerCuentaGrupo.html"


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions
        grupo = Grupo.objects.get(id = self.kwargs['idGrupo'])
        cuenta = CuentaGenerica.objects.get(id = self.kwargs['idCuenta'])

        context['grupo'] = grupo
        context['cuenta'] = cuenta
        return context

 
    def post(self, request, *args, **kwargs):
        grupo = Grupo.objects.get(id = self.kwargs['idGrupo'])
        cuenta = CuentaGenerica.objects.get(id = self.kwargs['idCuenta'])
        grupo.balance -= cambiarMoneda(cuenta.tipo_moneda, grupo.tipo_moneda, self.kwargs['saldo'])
        grupo.cuentas.remove(cuenta)
        grupo.save()
        return HttpResponseRedirect(reverse_lazy('cuentas:listarCuentasGrupo', kwargs = {'idGrupo' : kwargs['idGrupo'] }))


class GrupoDelete(DeleteView):
    model = Grupo
    template_name = 'grupos/eliminarGrupo.html'
    success_url = reverse_lazy("grupos:listarGrupos")