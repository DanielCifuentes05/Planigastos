from django import forms 
from .models import TransaccionBase, TIPO_TRANSACCION, TransaccionPresupuesto
from datetime import date
from planigastos.convertirMoneda import *
from Grupo.models import Grupo
from presupuesto.models import Presupuesto
from usuario.models import Usuario, User
import re
from django.core.mail import send_mail

def enviarMail(presupuesto, id_cuenta):
    if presupuesto.saldoConsumido/presupuesto.saldoTotal > 1:
        usuario = User.objects.get(id = id_cuenta)
        mssg = ("Hola " + usuario.first_name + " " + usuario.last_name +  
                ", tu presupuesto " + presupuesto.nombre + " se ha acabado \n\nAtte: Equipo Planigastos")
        send_mail(
            '¡Saldo de presupuesto agotado!',
            mssg,
            'planigastos@gmail.com',
            [usuario.email],
        )
    elif presupuesto.saldoConsumido/presupuesto.saldoTotal > 0.6:
        usuario = User.objects.get(id = id_cuenta)
        mssg = ("Hola " + usuario.first_name + " " + usuario.last_name +  
                ", tu presupuesto " + presupuesto.nombre + " está a punto de acabarse (" + 
                str(round(presupuesto.saldoConsumido*100/presupuesto.saldoTotal, 2)) + "%)\n\nAtte: Equipo Planigastos")
        send_mail(
            'Saldo de presupuesto a punto de acabarse',
            mssg,
            'planigastos@gmail.com',
            [usuario.email],
        )
class CrearTransaccionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.valorCuenta = kwargs.pop('valorCuenta')
        self.tipo_moneda = kwargs.pop('tipo_moneda')
        self.id_cuenta_generica = kwargs.pop('cuenta')
        self.id_usuario = kwargs.pop('idUsuario')
        super(CrearTransaccionForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        cleaned_data = super().clean ()
        valor_trans = cleaned_data.get("valor")
        tipo_trans = cleaned_data.get("tipoTransaccion")
        tipo_moneda = cleaned_data.get("tipo_moneda")
        #Si es un gasto y el saldo de la cuenta queda negativo 
        if valor_trans is not None:
            valor_trans_conver = cambiarMoneda(tipo_moneda, self.tipo_moneda, valor_trans)
            if tipo_trans == 2 and self.valorCuenta - valor_trans_conver < 0:
                msg = "Si realizas este gasto, la cuenta va a quedar con saldo negativo"
                self.add_error("valor", msg)


    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")
        if fecha > date.today():
            raise forms.ValidationError("La fecha de la transaccion no puede ser futura", code = "fecha")
        return fecha


    def save(self, commit=True):
        transaccion = super().save(commit=False)
        # do custom stuff

        valor = self.cleaned_data.get("valor")
        tipo_moneda = self.cleaned_data.get("tipo_moneda")
        tipo_trans = self.cleaned_data.get("tipoTransaccion")
        presupuestos = Presupuesto.objects.filter(cuentas__id = self.id_cuenta_generica)
        grupos = Grupo.objects.filter(cuentas__id = self.id_cuenta_generica)

        data = obtenerMonedas()
        for presupuesto in presupuestos:
            valor_final = cambiarMonedaJson(tipo_moneda, presupuesto.tipo_moneda, valor, data)
            if tipo_trans == 1:
                presupuesto.saldoConsumido -= valor_final
                #if presupuesto.saldoConsumido < 0:
                #    presupuesto.saldoConsumido = 0
            else:
                presupuesto.saldoConsumido += valor_final 
            
            enviarMail(presupuesto, self.id_usuario)
            presupuesto.save()  

        for grupo in grupos:
            print(grupo.nombre)
            valor_final = cambiarMonedaJson(tipo_moneda, presupuesto.tipo_moneda, valor, data)
            if tipo_trans == 1:
                grupo.balance += valor_final
            else:
                grupo.balance -= valor_final 
            grupo.save()   
        if commit:
            transaccion.save()
        return transaccion


    class Meta:
        model = TransaccionBase
        fields = [
            'nombre', 
            'tipoTransaccion',
            'valor',
            'tipo_moneda',
            'fecha',
            'descripcion',
            'icono', 
        ]

        widget = {
            'fecha' : forms.DateTimeInput(attrs={'class':'datepicker form-control', 'placeholder':'Selecciona una fecha'})
        }

        

class CrearTransaccionTarjetaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.limite = kwargs.pop('limite')
        self.valorCuenta = kwargs.pop('valorCuenta')
        self.tipo_moneda = kwargs.pop('tipo_moneda')
        self.id_cuenta_generica = kwargs.pop('cuenta')
        self.id_usuario = kwargs.pop('idUsuario')
        super().__init__(*args, **kwargs)
        
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")
        if fecha > date.today():
            raise forms.ValidationError("La fecha de la transaccion no puede ser futura", code = "fecha")
        return fecha


    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if len(nombre) == 0:
             raise forms.ValidationError("El nombre no puede estar vacío o solo con espacios", code = "nombre")
        x = re.match(r"((\S)*?(\s){2,}(\S)*?)+", nombre)
        #print(x)
        if x:
            raise forms.ValidationError("El nombre no puede tener dos o mas espacios seguidos", code = "nombre")
        return nombre

    def clean(self):
        cleaned_data = super().clean ()
        valor_trans = cleaned_data.get("valor")
        tipo_trans = cleaned_data.get("tipoTransaccion")
        tipo_moneda = cleaned_data.get("tipo_moneda")
        #Si es un gasto y el saldo de la cuenta queda negativo
        if valor_trans is not None:
            valor_trans_conver = cambiarMoneda(tipo_moneda, self.tipo_moneda, valor_trans)
            if tipo_trans == 2 and self.valorCuenta - valor_trans_conver < 0:
                msg = "Si realizas este gasto, la cuenta va a quedar con saldo negativo"
                self.add_error("valor", msg)

            elif tipo_trans == 1 and self.valorCuenta + valor_trans_conver > self.limite:
                msg = "No puedes ingresar un valor mas alto de lo que debes de tu tarjeta"
                self.add_error("valor", msg)
    

    def save(self, commit=True):
        transaccion = super().save(commit=False)
        # do custom stuff
        data = obtenerMonedas()
        valor = self.cleaned_data.get("valor")
        tipo_moneda = self.cleaned_data.get("tipo_moneda")
        tipo_trans = self.cleaned_data.get("tipoTransaccion")
        presupuestos = Presupuesto.objects.filter(cuentas__id = self.id_cuenta_generica)
        grupos = Grupo.objects.filter(cuentas__id = self.id_cuenta_generica)
        for presupuesto in presupuestos:
            print(presupuesto.nombre)
            valor_final = cambiarMonedaJson(tipo_moneda, presupuesto.tipo_moneda, valor, data)
            if tipo_trans == 1:
                presupuesto.saldoConsumido -= valor_final
                #if presupuesto.saldoConsumido < 0:
                #    presupuesto.saldoConsumido = 0
                presupuesto.save()
            else:
                presupuesto.saldoConsumido += valor_final 
                presupuesto.save()  

        for grupo in grupos:
            print(grupo.nombre)
            valor_final = cambiarMonedaJson(tipo_moneda, presupuesto.tipo_moneda, valor, data)
            if tipo_trans == 1:
                grupo.balance += valor_final
            else:
                grupo.balance -= valor_final 
            grupo.save()   
        if commit:
            transaccion.save()
        return transaccion

    
    class Meta:
        model = TransaccionBase
        fields = [
            'nombre', 
            'tipoTransaccion',
            'valor',
            'fecha',
            'descripcion',
            'icono', 
            'tipo_moneda'
        ]

        widget = {
            'fecha' : forms.DateTimeInput(attrs={'class':'datepicker form-control', 'placeholder':'Selecciona una fecha'})
        }

class CrearTransaccionAhorrosForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.saldo_minimo = kwargs.pop('saldo_minimo_req')
        self.valorCuenta = kwargs.pop('valorCuenta')
        self.tipo_moneda = kwargs.pop('tipo_moneda')
        self.id_cuenta_generica = kwargs.pop('cuenta')
        self.id_usuario = kwargs.pop('idUsuario')
        super().__init__(*args, **kwargs)
        
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")
        if fecha > date.today():
            raise forms.ValidationError("La fecha de la transaccion no puede ser futura", code = "fecha")
        return fecha
    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if len(nombre) == 0:
             raise forms.ValidationError("El nombre no puede estar vacío o solo con espacios", code = "nombre")
        x = re.match(r"((\S)*?(\s){2,}(\S)*?)+", nombre)
        #print(x)
        if x:
            raise forms.ValidationError("El nombre no puede tener dos o mas espacios seguidos", code = "nombre")
        return nombre
    def clean(self):
        cleaned_data = super().clean ()
        valor_trans = cleaned_data.get("valor")
        tipo_trans = cleaned_data.get("tipoTransaccion")
        tipo_moneda = cleaned_data.get("tipo_moneda")
        #Si es un gasto y el saldo de la cuenta queda negativo 
        if valor_trans is not None:
            valor_trans_conver = cambiarMoneda(tipo_moneda, self.tipo_moneda, valor_trans)
            if tipo_trans == 2:
                valor = self.valorCuenta - valor_trans_conver
                if valor < 0:
                    msg = "Si realizas este gasto, la cuenta va a quedar con saldo negativo"
                    self.add_error("valor", msg)
                elif valor < self.saldo_minimo:
                    msg = "Si realizas este gasto, la cuenta va a quedar con un saldo menor al minimo"
                    self.add_error("valor", msg)

    def save(self, commit=True):
        transaccion = super().save(commit=False)
        # do custom stuff
        data = obtenerMonedas()
        valor = self.cleaned_data.get("valor")
        tipo_moneda = self.cleaned_data.get("tipo_moneda")
        tipo_trans = self.cleaned_data.get("tipoTransaccion")
        presupuestos = Presupuesto.objects.filter(cuentas__id = self.id_cuenta_generica)
        for presupuesto in presupuestos:
            #print(presupuesto.nombre)
            valor_final = cambiarMonedaJson(tipo_moneda, presupuesto.tipo_moneda, valor, data)
            if tipo_trans == 1:
                presupuesto.saldoConsumido -= valor_final
                #if presupuesto.saldoConsumido < 0:
                #    presupuesto.saldoConsumido = 0
                presupuesto.save()
            else:
                presupuesto.saldoConsumido += valor_final 
                presupuesto.save()   

        for grupo in grupos:
            #print(grupo.nombre)
            valor_final = cambiarMonedaJson(tipo_moneda, presupuesto.tipo_moneda, valor, data)
            if tipo_trans == 1:
                grupo.balance += valor_final
            else:
                grupo.balance -= valor_final 
            grupo.save() 
        
        if commit:
            transaccion.save()
        return transaccion

    class Meta:
        model = TransaccionBase
        fields = [
            'nombre', 
            'tipoTransaccion',
            'valor',
            'fecha',
            'descripcion',
            'icono',
            'tipo_moneda' 
        ]

        widget = {
            'fecha' : forms.DateTimeInput(attrs={'class':'datepicker form-control', 'placeholder':'Selecciona una fecha'})
        }


class TransaccionPresupuestoForm(forms.ModelForm):
    presupuestoDestino = forms.ModelChoiceField(queryset = Presupuesto.objects.all())
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('usuario')
        self.presupuesto_origen = kwargs.pop('presupuesto_origen')

        super().__init__(*args, **kwargs)
        self.usuario = Usuario.objects.get(usuariodjango = self.user)
        presupuestos = Presupuesto.objects.filter(usuario=self.usuario)
        presupuestos2 = presupuestos.exclude(id = self.presupuesto_origen.id)
        self.fields['presupuestoDestino'].queryset = presupuestos2


    def clean(self):
        cleaned_data = super().clean ()
        valor = cleaned_data.get("valor")
        tipo_moneda = cleaned_data.get("tipo_moneda")

        if valor is not None:
            valor_origen = cambiarMoneda(tipo_moneda, self.presupuesto_origen.tipo_moneda, valor)
            valor_presupuesto = self.presupuesto_origen.saldoTotal - valor_origen
            if valor_presupuesto < 0:
                msg = "Si realizas esta transferencia, el presupuesto quedara con saldo maximo negativo"
                self.add_error("valor", msg)


    def save(self, commit=True):
        transaccion_presupuesto = super().save(commit=False)
        # do custom stuff

        destino = self.cleaned_data.get("presupuestoDestino")
        valor = self.cleaned_data.get("valor")
        tipo_moneda = self.cleaned_data.get("tipo_moneda")

        valor_origen = cambiarMoneda(tipo_moneda, self.presupuesto_origen.tipo_moneda, valor)
        valor_destino = cambiarMoneda(tipo_moneda, destino.tipo_moneda, valor)

        transaccion_presupuesto.presupuestoOrigen = self.presupuesto_origen
        self.presupuesto_origen.saldoTotal -= valor_origen
        self.presupuesto_origen.save() 

        enviarMail(self.presupuesto_origen, self.user.id)
        destino.saldoTotal += valor_destino
        destino.save()
        if commit:
            transaccion_presupuesto.save()
        return transaccion_presupuesto


    class Meta:
        model = TransaccionPresupuesto

        fields = [
            'presupuestoDestino', 
            'valor',
            'tipo_moneda'
        ]