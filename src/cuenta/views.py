from django.shortcuts import render
from .forms import (
    CuentaEfectivoForm, CuentaGenericaForm,
    TarjetaForm, PrestamoForm, AhorrosForm
)
from Grupo.models import Grupo
from .models import ( 
    CuentaEfectivo, CuentaGenerica, TarjetaCredito, CuentaPrestamo, 
    CuentaAhorros
    )
from django.views.generic import (
    CreateView, ListView, UpdateView,
    DeleteView, DetailView, FormView
)
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from usuario.models import Usuario
from transaccion.models import TransaccionBase
from presupuesto.models import Presupuesto

# Create your views here.

class CuentaGenericaCreate(CreateView):
    model = CuentaGenerica
    template_name = 'cuentas/crearCuentaGenerica.html'
    success_url = reverse_lazy("cuentas:listarCuentas")
    form_class = CuentaGenericaForm



    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        form = CuentaGenericaForm(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():
            cuenta = form.save()
            usuario = Usuario.objects.get(id = request.user.id)
            cuenta.usuario = usuario
            cuenta.save()
            return HttpResponseRedirect(self.success_url)
        else:
            for field in form:
                for error in field.errors:
                    print(error)
            return self.render_to_response(self.get_context_data(form = form))

# class ListarCuentas(ListView):
#     model = CuentaGenerica
#     template_name = 'cuentas/listarCuentas.html'
#     queryset = CuentaGenerica.objects.all()
#     paginate_by = 4

class ListarCuentasEfectivo(ListView):
    model = CuentaEfectivo
    template_name = 'cuentas/listarCuentas.html'
    
    paginate_by = 4

    def get_queryset(self):
        id_usuario = (Usuario.objects.get(usuariodjango_id = self.request.user.id)).id
        cuentas_usuario = CuentaGenerica.objects.filter(usuario_id = id_usuario)
        return CuentaEfectivo.objects.select_related('cuenta').filter(cuenta_id__in= cuentas_usuario)

class CuentaEfectivoCreate(CreateView):
    model = CuentaEfectivo
    template_name = 'cuentas/crearCuentaEfectivo.html'
    #template_name = 'cuentas/crearTemp.html'
    second_model = CuentaGenerica
    form_class = CuentaEfectivoForm
    second_form_class = CuentaGenericaForm
    success_url = reverse_lazy("cuentas:listarCuentas")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class
        if 'form2' not in context:
            context['form2'] = self.second_form_class
        return context

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     usuario = Usuario.objects.get(usuariodjango_id = request.user.id)
    #     kwargs.update({'usuario': usuario, 'grupo' : self.kwargs['pk']})
    #     return kwargs



    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST, request.FILES)
        print(form.is_valid(), form2.is_valid())
        if form.is_valid() and form2.is_valid():
            cuenta_efectivo = form.save(commit = False, buscarGrupos = False)
            cuenta_efectivo.cuenta = form2.save()
            usuario = Usuario.objects.get(usuariodjango_id = request.user.id)
            cuenta_efectivo.cuenta.usuario = usuario
            cuenta_efectivo.save()
            cuenta_efectivo.cuenta.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(request, self.template_name, {'form':form, 'form2':form2})

class CuentaEfectivoUpdate(UpdateView):
    model = CuentaGenerica
    second_model = CuentaEfectivo
    template_name = 'cuentas/modificarCuentaEfectivo.html'
    form_class = CuentaGenericaForm
    second_form_class = CuentaEfectivoForm

    def get_success_url(self):
        return reverse_lazy("cuentas:verCuenta", kwargs = {'pk' : self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super(CuentaEfectivoUpdate, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk', 0)
        cuenta_generica = self.model.objects.get(id = pk)
        cuenta_efectivo = self.second_model.objects.get(cuenta_id = pk)
        if 'form' not in context:
            context['form'] = self.form_class(instance = cuenta_generica)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(instance = cuenta_efectivo)
        context['id'] = pk
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        id_cuenta = kwargs.get('pk', 0)
        print(id_cuenta)
        cuenta_generica = self.model.objects.get(id = id_cuenta)
        cuenta_efectivo = self.second_model.objects.get(cuenta_id = id_cuenta)
        form = self.form_class(request.POST, request.FILES, instance = cuenta_generica)
        form2 = self.second_form_class(request.POST,  instance = cuenta_efectivo)
        print(form.is_valid(), form2.is_valid())
        if form.is_valid() and form2.is_valid():
            # cuenta_efectivo = form.save(commit = False)
            # cuenta_efectivo.cuenta = form2.save()
            # cuenta_efectivo.save()
            form.save()
            form2.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            for field in form2:
                for error in field.errors:
                    print(error)
            return self.render_to_response(self.get_context_data(form = form, form2 = form2))


class CuentaEfectivoView(DetailView):
    model = CuentaGenerica
    #model = CuentaEfectivo
    template_name = 'cuentas/verCuentaEfectivo.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions

        transacciones = TransaccionBase.objects.filter(cuenta_id = self.kwargs['pk'])
        context['transacciones'] = transacciones


        cuentaEfectivo = CuentaEfectivo.objects.get(cuenta_id = self.kwargs['pk'])
        context['cuentaEfectivo'] = cuentaEfectivo

        gruposPertenecientes= Grupo.objects.filter(cuentas__id = self.kwargs['pk'])
        context['gruposPertenecientes'] = gruposPertenecientes
        

        presupuestosPertenecientes= Presupuesto.objects.filter(cuentas__id = self.kwargs['pk'])
        context['presupuestosPertenecientes'] = presupuestosPertenecientes


        return context

class CuentaGenericaDelete(DeleteView):
    model = CuentaGenerica
    template_name = 'cuentas/eliminarCuenta.html'
    success_url = reverse_lazy("cuentas:listarCuentas")

##################################GRUPOS###########################
class ListarCuentasGrupo(ListView):
    model = CuentaGenerica
    template_name = 'cuentas/listarCuentasGrupo.html'
    
    paginate_by = 4



    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions

        context['grupo'] = Grupo.objects.get(id = self.kwargs['idGrupo'])
        return context

        
    def get_queryset(self):
        idGrupo = self.kwargs['idGrupo']
        grupo = Grupo.objects.get(id = idGrupo)
        id_cuentas_grupo = [cuenta.id for cuenta in grupo.cuentas.all()]
        efectivo = CuentaEfectivo.objects.filter(cuenta_id__in = id_cuentas_grupo).only("cuenta", "saldo_inicial")
        credito = TarjetaCredito.objects.filter(cuenta_id__in = id_cuentas_grupo).only("cuenta", "saldo_inicial")
        ahorros = CuentaAhorros.objects.filter(cuenta_id__in = id_cuentas_grupo).only("cuenta", "saldo_inicial")
        qs = efectivo.union(credito, ahorros)
        for q in qs:
            print(q.cuenta.nombre)
        return qs
        #return grupo.cuentas.all()


######TARJETAS DE CREDITO#########################

class ListarTarjetas(ListView):
    model = TarjetaCredito
    template_name = 'tarjetaCredito/listarTarjetas.html'
    
    paginate_by = 4

    def get_queryset(self):
        usuario = (Usuario.objects.get(usuariodjango = self.request.user))
        cuentas_usuario = CuentaGenerica.objects.filter(usuario = usuario)
        return TarjetaCredito.objects.select_related('cuenta').filter(cuenta_id__in= cuentas_usuario)

class TarjetaCreate(CreateView):
    model = TarjetaCredito
    template_name = 'tarjetaCredito/crearTarjeta.html'
    form_class = TarjetaForm
    second_form_class = CuentaGenericaForm
    success_url = reverse_lazy("cuentas:listarTarjetas")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class
        if 'form2' not in context:
            context['form2'] = self.second_form_class
        return context


    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST, request.FILES)
        print(form.is_valid(), form2.is_valid())
        if form.is_valid() and form2.is_valid():
            tarjeta = form.save(commit = False, buscarGrupos=False)
            tarjeta.cuenta = form2.save()
            
            usuario = Usuario.objects.get(usuariodjango_id = request.user.id)
            tarjeta.cuenta.usuario = usuario
            tarjeta.save()
            tarjeta.cuenta.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(request, self.template_name, {'form':form, 'form2':form2})

class TarjetaView(DetailView):
    model = CuentaGenerica
    #model = CuentaEfectivo
    template_name = 'tarjetaCredito/verTarjeta.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions

        transacciones = TransaccionBase.objects.filter(cuenta_id = self.kwargs['pk'])
        context['transacciones'] = transacciones


        tarjeta = TarjetaCredito.objects.get(cuenta_id = self.kwargs['pk'])
        context['tarjeta'] = tarjeta

        gruposPertenecientes= Grupo.objects.filter(cuentas__id = self.kwargs['pk'])
        context['gruposPertenecientes'] = gruposPertenecientes
        
        return context



class TarjetaUpdate(UpdateView):
    model = CuentaGenerica
    second_model = TarjetaCredito
    template_name = 'tarjetaCredito/modificarTarjeta.html'
    form_class = CuentaGenericaForm
    second_form_class = TarjetaForm

    def get_success_url(self):
        return reverse_lazy("cuentas:verTarjeta", kwargs = {'pk' : self.kwargs.get("pk")})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk', 0)
        cuenta_generica = self.model.objects.get(id = pk)
        cuenta_efectivo = self.second_model.objects.get(cuenta_id = pk)
        if 'form' not in context:
            context['form'] = self.form_class(instance = cuenta_generica)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(instance = cuenta_efectivo)
        context['id'] = pk
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        id_cuenta = kwargs.get('pk', 0)
        print(id_cuenta)
        cuenta_generica = self.model.objects.get(id = id_cuenta)
        cuenta_efectivo = self.second_model.objects.get(cuenta_id = id_cuenta)
        form = self.form_class(request.POST, request.FILES, instance = cuenta_generica)
        form2 = self.second_form_class(request.POST,  instance = cuenta_efectivo)
        print(form.is_valid(), form2.is_valid())
        if form.is_valid() and form2.is_valid():
            
            form.save()
            form2.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            for field in form2:
                for error in field.errors:
                    print(error)
            return self.render_to_response(self.get_context_data(form = form, form2 = form2))



class TarjetaDelete(DeleteView):
    model = CuentaGenerica
    template_name = 'cuentas/eliminarCuenta.html'
    success_url = reverse_lazy("cuentas:listarTarjetas")




#####CUENTAS DE PRESTAMO#####

class ListarPrestamo(ListView):
    model = CuentaPrestamo
    template_name = 'prestamos/listarPrestamo.html'
    
    paginate_by = 4


    def get_queryset(self):
        usuario = (Usuario.objects.get(usuariodjango = self.request.user))
        cuentas_usuario = CuentaGenerica.objects.filter(usuario = usuario)
        return CuentaPrestamo.objects.select_related('cuenta').filter(cuenta_id__in= cuentas_usuario)
       

class PrestamoCreate(CreateView):
    model = CuentaPrestamo
    template_name = 'prestamos/crearPrestamo.html'
    form_class = PrestamoForm
    second_form_class = CuentaGenericaForm
    success_url = reverse_lazy("cuentas:listarPrestamo")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class
        if 'form2' not in context:
            context['form2'] = self.second_form_class
        return context


    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST, request.FILES)
        print(form.is_valid(), form2.is_valid())
        if form.is_valid() and form2.is_valid():
            prestamo = form.save(commit = False)
            prestamo.cuenta = form2.save()
            usuario = Usuario.objects.get(usuariodjango_id = request.user.id)
            prestamo.cuenta.usuario = usuario
            prestamo.save()
            prestamo.cuenta.save()
            self.idPrestamo = prestamo.id
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(request, self.template_name, {'form':form, 'form2':form2})


class SuccessPrestamoView(DetailView):
    model = CuentaPrestamo
    #model = CuentaEfectivo
    template_name = 'prestamos/successPrestamo.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions
        
        cuentaPrestamo = CuentaPrestamo.objects.get(id = self.kwargs['pk'])
        print(cuentaPrestamo.montoNeto)
        context['cuentaPrestamo'] = cuentaPrestamo
        return context


class PrestamoDelete(DeleteView):
    model = CuentaGenerica
    template_name = 'cuentas/eliminarCuenta.html'
    success_url = reverse_lazy("cuentas:listarPrestamo")


#Por ahora no se realiza un update de prestamo porque cambiaria todo, mejor borrarlo y crearlo ora vez


#####CUENTAS DE AHORROS#########


class ListarAhorros(ListView):
    model = CuentaAhorros
    template_name = 'ahorros/listarCuentas.html'
    
    paginate_by = 4

    def get_queryset(self):
        usuario = (Usuario.objects.get(usuariodjango = self.request.user))
        cuentas_usuario = CuentaGenerica.objects.filter(usuario = usuario)
        return CuentaAhorros.objects.select_related('cuenta').filter(cuenta_id__in= cuentas_usuario)

class AhorrosCreate(CreateView):
    model = CuentaAhorros
    template_name = 'ahorros/crearCuenta.html'
    form_class = AhorrosForm
    second_form_class = CuentaGenericaForm
    success_url = reverse_lazy("cuentas:listarAhorros")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class
        if 'form2' not in context:
            context['form2'] = self.second_form_class
        return context



        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST, request.FILES)
        if form.is_valid() and form2.is_valid():
            ahorros = form.save(commit = False, buscarGrupos=False)
            ahorros.cuenta = form2.save()
            
            usuario = Usuario.objects.get(usuariodjango_id = request.user.id)
            ahorros.cuenta.usuario = usuario
            ahorros.save()
            ahorros.cuenta.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(request, self.template_name, context = {'form':form, 'form2':form2})

class AhorrosView(DetailView):
    model = CuentaGenerica
    #model = CuentaEfectivo
    template_name = 'ahorros/verCuenta.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet all the transactions

        # transacciones = TransaccionBase.objects.filter(cuenta_id = self.kwargs['pk'])
        # context['transacciones'] = transacciones


        ahorros = CuentaAhorros.objects.get(cuenta_id = self.kwargs['pk'])
        context['ahorros'] = ahorros

        gruposPertenecientes= Grupo.objects.filter(cuentas__id = self.kwargs['pk'])
        context['gruposPertenecientes'] = gruposPertenecientes
        
        return context



class AhorrosUpdate(UpdateView):
    model = CuentaGenerica
    second_model = CuentaAhorros
    template_name = 'ahorros/modificarCuenta.html'
    form_class = CuentaGenericaForm
    second_form_class = AhorrosForm

    def get_success_url(self):
        return reverse_lazy("cuentas:verAhorros", kwargs = {'pk' : self.kwargs.get("pk")})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk', 0)
        cuenta_generica = self.model.objects.get(id = pk)
        cuenta_ahorros = self.second_model.objects.get(cuenta_id = pk)
        if 'form' not in context:
            context['form'] = self.form_class(instance = cuenta_generica)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(instance = cuenta_ahorros)
        context['id'] = pk
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        id_cuenta = kwargs.get('pk', 0)
        cuenta_generica = self.model.objects.get(id = id_cuenta)
        cuenta_ahorros = self.second_model.objects.get(cuenta_id = id_cuenta)
        form = self.form_class(request.POST, request.FILES, instance = cuenta_generica)
        form2 = self.second_form_class(request.POST,  instance = cuenta_ahorros)
        print(form.is_valid(), form2.is_valid())
        if form.is_valid() and form2.is_valid():
            
            form.save()
            form2.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            for field in form2:
                for error in field.errors:
                    print(error)
            return self.render_to_response(self.get_context_data(form = form, form2 = form2))



class AhorrosDelete(DeleteView):
    model = CuentaGenerica
    template_name = 'cuentas/eliminarCuenta.html'
    success_url = reverse_lazy("cuentas:listarAhorros")


from django.shortcuts import get_list_or_404
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import  inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import csv
def exportarCuentaCSV(request, **kwargs):
    # Create the HttpResponse object with the appropriate CSV header.
    transacciones = TransaccionBase.objects.filter(cuenta_id = kwargs.get("pk"))
    response = HttpResponse (content_type = 'text/csv')
    response[ 'Content-Disposition' ] = 'attachment; filename="transacciones.csv"'


    writer = csv.writer(response)
    writer.writerow (['Nombre', 'Tipo', 'Moneda', 'Valor', 'Descripcion', 'Fecha'])
    for transaccion in transacciones:
        tipo = ""
        if transaccion.tipoTransaccion == 1:
            tipo = "Ingreso"
        else:
            tipo = "Gasto"
        writer.writerow ([transaccion.nombre, 
                        tipo, 
                        transaccion.tipo_moneda, 
                        str(transaccion.valor), 
                        transaccion.descripcion, 
                        (transaccion.fecha).strftime("%m/%d/%Y")])

    return response

def exportarCuentaPDF(request, **kwargs):
    transacciones = TransaccionBase.objects.filter(cuenta_id = kwargs.get("pk"))
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    data = [['Nombre', 'Tipo', 'Moneda', 'Valor', 'Descripcion', 'Fecha']]
    x = 10
    y = 800
    for transaccion in transacciones:
        y -= 0.3*inch
        tipo = ""
        if transaccion.tipoTransaccion == 1:
            tipo = "Ingreso"
        else:
            tipo = "Gasto"
        data.append([transaccion.nombre, 
                        tipo, 
                        transaccion.tipo_moneda, 
                        str(transaccion.valor), 
                        transaccion.descripcion, 
                        (transaccion.fecha).strftime("%m/%d/%Y")])
    width = 700
    height = 200
    
    f = Table(data, 6*[1.3*inch], (len(transacciones) + 1)*[0.3*inch])
    f.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.gray),
                       ('TEXTCOLOR',(0,0),(-1, 0),colors.red)
                    ])
                       )
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


def exportarPrestamoPDF(request, **kwargs):
    prestamo = CuentaPrestamo.objects.get(id = kwargs.get("pk"))
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    data = [['Nombre', 'Moneda', 'Monto Neto', 
            'Meses', 'TAE', 'Interes', 
            'Ultimo Pago', 'Pago Mensual', 'Meses Pagados']]
    
    data.append([prestamo.cuenta.nombre, 
                    prestamo.cuenta.tipo_moneda, 
                    str(prestamo.montoNeto), 
                    str(prestamo.mesesPago), 
                    str(prestamo.TAE) + "%",
                    str(prestamo.interesNominal) + "%",
                    (prestamo.ultimoPago).strftime("%m/%d/%Y"),
                    str(prestamo.pagoMensual), 
                    str(prestamo.mesesPagados)])
    width = 700
    height = 200
    x = 10
    y = 800
    colWidth = [inch, 0.6*inch, inch, 0.6*inch, 0.6*inch, 0.6*inch, inch, inch, 1.2*inch]
    f = Table(data, colWidth, 2*[0.3*inch])
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
    return FileResponse(buffer, as_attachment=True, filename='prestamo.pdf')


from datetime import datetime

def pagarMesPrestamo(request, **kwargs):
    prestamo = CuentaPrestamo.objects.get(id = kwargs.get("pk"))
    if prestamo.mesesPagados < prestamo.mesesPago:
        prestamo.mesesPagados += 1
        prestamo.ultimoPago = datetime.now()
        saldo = prestamo.saldoPendiente - prestamo.pagoMensual
        if saldo < 0:
            saldo = 0
        prestamo.saldoPendiente = saldo
        prestamo.save()
    return render(request, template_name = "prestamos/successPrestamo.html", context={'cuentaPrestamo' : prestamo})