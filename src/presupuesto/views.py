from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView, ListView, DetailView, UpdateView, 
    DeleteView, TemplateView
)
from django.urls import reverse_lazy
from .models import Presupuesto
from usuario.models import Usuario
from .forms import PresupuestoForm, PresupuestoForm2
from transaccion.models import TransaccionBase
from cuenta.models import CuentaGenerica
import datetime
# Create your views here.
class CrearPresupuesto(CreateView):
    model = Presupuesto
    form_class = PresupuestoForm
    template_name = "presupuestos/crearPresupuesto.html"
    success_url = reverse_lazy("presupuesto:listarPresupuestos")


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'usuario': self.request.user})
        return kwargs

class ListarPresupuestos(ListView):
    model = Presupuesto
    template_name = 'presupuestos/listarPresupuestos.html'
    paginate_by = 4

    def get_queryset(self):
        id_usuario = (Usuario.objects.get(usuariodjango_id = self.request.user.id)).id
        #presupuestos_usuario = Presupuesto.objects.filter(usuario_id = id_usuario)
        return Presupuesto.objects.filter(usuario_id = id_usuario)

class VerPresupuesto(DetailView):
    model = Presupuesto
    template_name = "presupuestos/verPresupuesto.html"


    def porcentajeTiempo(self, presupuesto):
        fecha_inicio = presupuesto.fechaInicio
        now = datetime.datetime.now()
        now2 = datetime.date(now.year, now.month, now.day)
        #print(now2, fecha_inicio)
        delta_actual = (now2 - fecha_inicio).days 
        
        anioFin = fecha_inicio.year + presupuesto.duracion // 12
        mesFin = fecha_inicio.month + presupuesto.duracion % 12
        if mesFin > 12:
            anioFin += 1
            mesFin = mesFin - 12
        fechaFin = datetime.date(anioFin, mesFin, 1)
        delta_fin = (fechaFin - fecha_inicio).days

        porcentaje = round((delta_actual/delta_fin)*100, 2)
        return porcentaje


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cuentasPertenecientes = Presupuesto.objects.get(id = self.kwargs['pk'])
        cuentasPertenecientes = cuentasPertenecientes.cuentas.all()
        presupuesto = Presupuesto.objects.get(id = self.kwargs['pk'])
        context['porcentajeTiempo'] = self.porcentajeTiempo(presupuesto)
        context['porcentajeDinero'] = round(presupuesto.saldoConsumido*100/presupuesto.saldoTotal, 2)
        context['cuentasPertenecientes'] = cuentasPertenecientes
        
        return context
    
   
    
class ModificarPresupuesto(UpdateView):
    model = Presupuesto
    template_name = "presupuestos/modificarPresupuesto.html"
    form_class= PresupuestoForm2
    success_url=reverse_lazy("presupuesto:listarPresupuestos")


    def get_success_url(self):
        return reverse_lazy('presupuesto:verPresupuesto', kwargs = {'pk' : self.kwargs['pk'] })


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'usuario': self.request.user, 'presupuesto' : self.kwargs['pk']})
        return kwargs

class EliminarPresupuesto(DeleteView):
    model = Presupuesto
    template_name = 'presupuestos/eliminarPresupuesto.html'
    success_url = reverse_lazy("presupuesto:listarPresupuestos")

class ListarCuentaPresupuesto(ListView):
    model = Presupuesto
    template_name = 'presupuestos/listarCuentaPresupuestos.html'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions

        context['presupuesto'] = Presupuesto.objects.get(id = self.kwargs['pk'])
        return context

        
    def get_queryset(self):
        pk = self.kwargs['pk']
        presupuesto = Presupuesto.objects.get(id = pk)
        #print(type(grupo), type(grupo.cuentas))
        return presupuesto.cuentas.all()

class ListarCuentaPresupuestoL(ListView):
    model = Presupuesto
    template_name = 'presupuestos/listarCuentaPresupuestosL.html'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions

        context['presupuesto'] = Presupuesto.objects.get(id = self.kwargs['pk'])
        return context

        
    def get_queryset(self):
        pk = self.kwargs['pk']
        presupuesto = Presupuesto.objects.get(id = pk)
        #print(type(grupo), type(grupo.cuentas))
        return presupuesto.cuentas.all() 


class RemoveCuentaPresupuesto(TemplateView):
    model = Presupuesto
    template_name = "presupuestos/removerCuentaPresupuesto.html"


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions
        presupuesto = Presupuesto.objects.get(id = self.kwargs['idPresupuesto'])
        cuenta = CuentaGenerica.objects.get(id = self.kwargs['idCuenta'])

        context['presupuesto'] = presupuesto
        context['cuenta'] = cuenta
        return context

 
    def post(self, request, *args, **kwargs):
        presupuesto = Presupuesto.objects.get(id = self.kwargs['idPresupuesto'])
        cuenta = CuentaGenerica.objects.get(id = self.kwargs['idCuenta'])
        presupuesto.cuentas.remove(cuenta)
        presupuesto.save()
        return HttpResponseRedirect(reverse_lazy('presupuesto:listarCuentaPresupuestosL', 
                                                    kwargs = {'pk' : kwargs['idPresupuesto'] }))
    