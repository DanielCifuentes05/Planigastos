from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    CreateView, ListView, UpdateView, 
    DeleteView, TemplateView, DetailView
)
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import  inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from .models import TransaccionBase, TransaccionPresupuesto#, ArchivosTransaccion
from django.urls import reverse_lazy, reverse
from cuenta.models import CuentaGenerica, CuentaEfectivo, TarjetaCredito, CuentaAhorros
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from .forms import *
from datetime import datetime
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from planigastos.convertirMoneda import cambiarMoneda
from presupuesto.models import Presupuesto
import csv
import tempfile
from datetime import datetime
# Create your views here.



class ListarTransacciones(ListView):
    template_name = 'transacciones/listarTransacciones.html'
    paginate_by = 4
    def get_queryset(self, *args, **kwargs):
        return TransaccionBase.objects.filter(cuenta_id = self.kwargs['cuenta']).order_by('-id')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions

        
        context['cuenta'] = self.kwargs['cuenta']
        return context

def getKeySort(item):
    return item[1]

def exportarTransaccion(request, **kwargs):
    # Create the HttpResponse object with the appropriate CSV header.
    transaccion = get_object_or_404(TransaccionBase, pk = kwargs.get("pk")) 
    response = HttpResponse (content_type = 'text/csv')
    response[ 'Content-Disposition' ] = 'attachment; filename="transaccion.csv"'

    writer = csv.writer(response)
    writer.writerow (['Nombre', 'Tipo', 'Moneda', 'Valor', 'Descripcion', 'Fecha'])
    writer.writerow ([transaccion.nombre, 
                    transaccion.tipoTransaccion, 
                    transaccion.tipo_moneda, 
                    str(transaccion.valor), 
                    transaccion.descripcion, 
                    (transaccion.fecha).strftime("%m/%d/%Y")])

    return response


def exportarTransaccionPDF(request, **kwargs):
    transaccion = get_object_or_404(TransaccionBase, pk = kwargs.get("pk"))
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    data = [['Nombre', 'Tipo', 'Moneda', 'Valor', 'Descripcion', 'Fecha'],
    [transaccion.nombre, 
                    transaccion.tipoTransaccion, 
                    transaccion.tipo_moneda, 
                    str(transaccion.valor), 
                    transaccion.descripcion, 
                    (transaccion.fecha).strftime("%m/%d/%Y")]]
    width = 700
    height = 200
    x = 10
    y = 600
    f = Table(data, 6*[1.3*inch], 2*[0.5*inch])
    f.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.gray),
                       ('TEXTCOLOR',(0,0),(-1, 0),colors.red)]))
    f.wrapOn(p, width, height)
    f.drawOn(p, x, y)
    #p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='transaccion.pdf')
    
class ListarTransaccionesOrden(ListView):
    template_name = 'transacciones/listarTransacciones.html'
    paginate_by = 4
    

    # def ordenarQuery(self, queryset, tipo):
    #     querysetNuevo = []
    #     for transaccion in queryset:
    #         print("en el for")
    #         valor = transaccion.valor
    #         if tipo == "descendente":
    #             valor = valor * -1
            
    #         querysetNuevo.append((transaccion, cambiarMoneda(transaccion.tipo_moneda, 'COP', transaccion.valor)))
    #     print("fuera del for")
    #     querysetNuevo = sorted(querysetNuevo, key=getKeySort)
    #     querysetNuevo = (i[0] for i in querysetNuevo)
    #     return querysetNuevo

    def get_queryset(self, *args, **kwargs):
        filtro = self.kwargs.get("orden", "id")
        queryset = TransaccionBase.objects.filter(cuenta_id = self.kwargs['cuenta'])
        if filtro == "fechaReciente":
            queryset = queryset.order_by('-fecha')
        elif filtro == "fechaAntigua":
            queryset = queryset.order_by('fecha')
        elif filtro == "valorAlto":
            queryset = queryset.order_by('-valor')
        elif filtro == "valorBajo":
            queryset = queryset.order_by('valor')
        else:
            queryset = queryset.order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions
        context['cuenta'] = self.kwargs['cuenta']
        return context



    


class CrearTransaccion(CreateView):
    model = TransaccionBase
    template_name = 'transacciones/crearTransaccion.html'
    form_class = CrearTransaccionForm
    #success_url = reverse_lazy("cuentas:verCuenta")

    def get_form_kwargs(self):
        kwargs = super(CrearTransaccion, self).get_form_kwargs()
        cuenta = CuentaEfectivo.objects.get(cuenta_id = self.kwargs['cuenta'])
        valorCuenta = cuenta.saldo_inicial
        tipo_moneda = cuenta.cuenta.tipo_moneda
        kwargs.update({'valorCuenta': valorCuenta, 'tipo_moneda': tipo_moneda, 
                        'cuenta' : self.kwargs['cuenta'], 
                        'idUsuario' : self.request.user.id})
        return kwargs

    def get_success_url(self):
        return reverse_lazy('cuentas:verCuenta', kwargs = {'pk' : self.kwargs['cuenta'] })


    def actualizarSaldo(self, cuenta, form):
        cuentaEfectivo = CuentaEfectivo.objects.get(cuenta = cuenta)
        saldo = cuentaEfectivo.saldo_inicial
        valor = cambiarMoneda(form.cleaned_data['tipo_moneda'], cuentaEfectivo.cuenta.tipo_moneda, 
                                  form.cleaned_data['valor'])
        if form.cleaned_data['tipoTransaccion'] == 1:
            saldo += valor
        else:
            saldo -= valor
        cuentaEfectivo.saldo_inicial = saldo
        cuentaEfectivo.save()
        

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        cuenta = CuentaEfectivo.objects.get(cuenta_id = self.kwargs['cuenta'])
        valorCuenta = cuenta.saldo_inicial
        tipo = cuenta.cuenta.tipo_moneda
        form = self.form_class(request.POST, request.FILES, valorCuenta = valorCuenta, 
                                tipo_moneda = tipo, 
                                cuenta = self.kwargs['cuenta'], idUsuario = self.request.user.id)
        # for error in  form.errors:
        #     print("error: ",error)
        if form.is_valid():
            transaccion = form.save(commit = False)

            #Actualizar el saldo de la cuenta 
            cuenta = CuentaGenerica.objects.get(id = self.kwargs['cuenta'])

            self.actualizarSaldo(cuenta, form)

            #Guardar la cuenta a la que pertenece la transaccion
            transaccion.cuenta = cuenta
            transaccion.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form = form))


# class TransaccionUpdate(UpdateView):
#     model = TransaccionBase
#     template_name = 'transacciones/modificarTransaccion.html'
#     form_class = CrearTransaccionForm
#     success_url = reverse_lazy("cuentas:listarCuentas")


class TransaccionDelete(DeleteView):
    model = TransaccionBase
    template_name = 'transacciones/eliminarTransaccion.html'
    

    def get_success_url(self):
        return reverse_lazy('transacciones:listarTransacciones', kwargs = {'cuenta' : self.cuentaSelf.id })

    def post(self, request, *args, **kwargs):

        self.object = self.get_object
        
        id_transaccion = kwargs.get('pk', 0)
        transaccion = TransaccionBase.objects.get(id = id_transaccion)
        cuenta = CuentaEfectivo.objects.get(cuenta = transaccion.cuenta)
        self.cuentaSelf = transaccion.cuenta
        valor = transaccion.valor
        if transaccion.tipoTransaccion == 1:
            valor = -1*valor
        cuenta.saldo_inicial += valor
        cuenta.save()
        transaccion.delete()
        return HttpResponseRedirect(self.get_success_url())

#####TARJETA DE CREDITO 


class CrearTransaccionTarjeta(CreateView):
    model = TransaccionBase
    template_name = 'transacciones/crearTransaccion.html'
    form_class = CrearTransaccionTarjetaForm
    #success_url = reverse_lazy("cuentas:verCuenta")



    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tarjeta = (TarjetaCredito.objects.get(cuenta_id = self.kwargs['cuenta']))
        limite = tarjeta.limite
        valorCuenta = tarjeta.saldo_inicial
        tipo_moneda = tarjeta.cuenta.tipo_moneda
        kwargs.update({'valorCuenta': valorCuenta, 'tipo_moneda': tipo_moneda, 
                        'limite' : limite, 'cuenta' : self.kwargs['cuenta'], 
                        'idUsuario' : self.request.user.id})
        return kwargs


    def get_success_url(self):
        return reverse_lazy('cuentas:verTarjeta', kwargs = {'pk' : self.kwargs['cuenta'] })


    def actualizarSaldo(self, cuenta, form):
        tarjeta = TarjetaCredito.objects.get(cuenta = cuenta)
        saldo = tarjeta.saldo_inicial
        pasivos = tarjeta.pasivos
        valor = cambiarMoneda(form.cleaned_data['tipo_moneda'], tarjeta.cuenta.tipo_moneda, 
                                  form.cleaned_data['valor'])
        #print("saldo inicial", saldo)
        if form.cleaned_data['tipoTransaccion'] == 1:
            saldo += valor
            pasivos -= valor

        else:
            saldo -= valor
            pasivos += valor

        #print("NUEVO SALDO", saldo)
        tarjeta.saldo_inicial = saldo
        tarjeta.pasivos = pasivos
        tarjeta.save()



    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        tarjeta = (TarjetaCredito.objects.get(cuenta_id = self.kwargs['cuenta']))
        limite = tarjeta.limite
        valorCuenta = tarjeta.saldo_inicial
        tipo = tarjeta.cuenta.tipo_moneda
        form = self.form_class(request.POST, request.FILES, valorCuenta = valorCuenta, limite = limite, 
                                tipo_moneda = tipo, cuenta = self.kwargs['cuenta'], 
                                idUsuario = self.request.user.id)
        # for error in  form.errors:
        #     print("error: ",error)
        if form.is_valid():
            transaccion = form.save(commit = False)

            #Actualizar el saldo de la cuenta 
            cuenta = CuentaGenerica.objects.get(id = self.kwargs['cuenta'])
            self.actualizarSaldo(cuenta, form)

            #Guardar la cuenta a la que pertenece la transaccion
            transaccion.cuenta = cuenta
            transaccion.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form = form))


class ListarTransaccionesTarjeta(ListView):
    template_name = 'transacciones/listarTransaccionesT.html'
    paginate_by = 4
    def get_queryset(self, *args, **kwargs):
        return TransaccionBase.objects.filter(cuenta_id = self.kwargs['cuenta']).order_by('-id')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions
        context['cuenta'] = self.kwargs['cuenta']
        return context


#####CUENTA DE AHORROS################3


class CrearTransaccionAhorros(CreateView):
    model = TransaccionBase
    template_name = 'transacciones/crearTransaccion.html'
    form_class = CrearTransaccionAhorrosForm
    #success_url = reverse_lazy("cuentas:verCuenta")



    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        ahorros = (CuentaAhorros.objects.get(cuenta_id = self.kwargs['cuenta']))
        saldo_minimo = ahorros.saldo_minimo_req
        valorCuenta = ahorros.saldo_inicial
        tipo_moneda = ahorros.cuenta.tipo_moneda
        kwargs.update({'valorCuenta': valorCuenta, 'saldo_minimo_req' : saldo_minimo, 
                        'tipo_moneda':tipo_moneda, 'cuenta' : self.kwargs['cuenta'],
                        'idUsuario' : self.request.user.id
                        })
        return kwargs


    def get_success_url(self):
        return reverse_lazy('cuentas:verAhorros', kwargs = {'pk' : self.kwargs['cuenta'] })


    def actualizarSaldo(self, cuenta, form):
        ahorros = CuentaAhorros.objects.get(cuenta = cuenta)
        saldo = ahorros.saldo_inicial
        valor = cambiarMoneda(form.cleaned_data['tipo_moneda'], ahorros.cuenta.tipo_moneda, 
                                  form.cleaned_data['valor'])
        if form.cleaned_data['tipoTransaccion'] == 1:
            saldo += valor
        else:
            saldo -= valor
        ahorros.saldo_inicial = saldo
        ahorros.save()


    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        ahorros = (CuentaAhorros.objects.get(cuenta_id = self.kwargs['cuenta']))
        saldo_minimo = ahorros.saldo_minimo_req
        valorCuenta = ahorros.saldo_inicial
        tipo = ahorros.cuenta.tipo_moneda
        form = self.form_class(request.POST, request.FILES, valorCuenta = valorCuenta, 
                                saldo_minimo_req = saldo_minimo, tipo_moneda = tipo, 
                                cuenta = self.kwargs['cuenta'], idUsuario = self.request.user.id)
        if form.is_valid():
            transaccion = form.save(commit = False)

            #Actualizar el saldo de la cuenta 
            cuenta = CuentaGenerica.objects.get(id = self.kwargs['cuenta'])
            self.actualizarSaldo(cuenta, form)

            #Guardar la cuenta a la que pertenece la transaccion
            transaccion.cuenta = cuenta
            transaccion.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form = form))


class ListarTransaccionesAhorros(ListView):
    template_name = 'transacciones/listarTransaccionesP.html'
    paginate_by = 4
    def get_queryset(self, *args, **kwargs):
        return TransaccionBase.objects.filter(cuenta_id = self.kwargs['cuenta']).order_by('-id')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions
        context['cuenta'] = self.kwargs['cuenta']
        return context



###TRANSACCIONES ENTRE PRESUPUESTOS####

class TransaccionPresupuestoCreate(CreateView):
    model = TransaccionPresupuesto
    template_name = "presupuestos/crearTransaccionPresupuesto.html"
    form_class = TransaccionPresupuestoForm



    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        presupuesto_origen = Presupuesto.objects.get(id = self.kwargs['cuenta'])
        kwargs.update({'usuario': self.request.user, 'presupuesto_origen' : presupuesto_origen})
        return kwargs


    def get_success_url(self):
        return reverse_lazy('presupuesto:verPresupuesto', kwargs = {'pk' : self.kwargs['cuenta'] })

    

    

