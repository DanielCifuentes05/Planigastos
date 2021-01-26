from django import forms 
from .models import (
    CuentaEfectivo, CuentaGenerica,
    TarjetaCredito, CuentaPrestamo,
    CuentaAhorros
) 
from usuario.models import Usuario
from datetime import date
import re
from Grupo.models import Grupo
from planigastos.convertirMoneda import obtenerMonedas, cambiarMonedaJson
from planigastos.tipoMoneda import TIPO_MONEDA

class CuentaGenericaForm(forms.ModelForm):


    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if len(nombre) == 0:
             raise forms.ValidationError("El nombre no puede estar vacío o solo con espacios", code = "nombre")
        x = re.match(r"((\S)*?(\s){2,}(\S)*?)+", nombre)
        #print(x)
        if x:
            raise forms.ValidationError("El nombre no puede tener dos o mas espacios seguidos", code = "nombre")
        return nombre


    class Meta:
        model = CuentaGenerica
        #tipo_moneda = forms.MultipleChoiceField(choices = TIPO_MONEDA)
        #icono = forms.ImageField()
        fields = [
            'nombre', 
            'icono', 
            'tipo_moneda'
        ]


class CuentaEfectivoForm(forms.ModelForm):

    def save(self, commit = True, buscarGrupos = True):
        efectivo = super().save(commit=False)
        saldo_nuevo = self.cleaned_data["saldo_inicial"]

        if buscarGrupos:
            grupos = Grupo.objects.filter(cuentas__id = efectivo.cuenta.id)
            if grupos.exists():
                saldo_anterior = CuentaEfectivo.objects.get(id = efectivo.id)
                saldo_anterior = saldo_anterior.saldo_inicial
                data = obtenerMonedas()
                for grupo in grupos:
                    grupo.balance -= cambiarMonedaJson(efectivo.cuenta.tipo_moneda, grupo.tipo_moneda, saldo_anterior, data)
                    grupo.balance += cambiarMonedaJson(efectivo.cuenta.tipo_moneda, grupo.tipo_moneda, saldo_nuevo, data)
                    grupo.save()
        if commit: 
            efectivo.save()
        return efectivo


    class Meta:
        model = CuentaEfectivo
        fields = [
            'saldo_inicial'
        ]

class TarjetaForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean ()
        pasivos = cleaned_data.get("pasivos")
        limite = cleaned_data.get("limite")
        cuota_manejo = cleaned_data.get("cuota_manejo")
        
        if pasivos is not None and limite is not None and pasivos > limite:
            msg = "El valor de tus pasivos no puede ser mayor al limite de la tarjeta"
            self.add_error("pasivos", msg)
        if cuota_manejo is not None and limite is not None and cuota_manejo > 0.2 * limite:
            msg = "El valor de la cuota de manejo no puede ser mayor al 20% del limite de la tarjeta"
            self.add_error("cuota_manejo", msg)

    def save(self, commit = True, buscarGrupos = True):
        tarjeta = super().save(commit=False)

        limite = self.cleaned_data["limite"]
        pasivos = self.cleaned_data["pasivos"]
        tarjeta.saldo_inicial = limite - pasivos
        if buscarGrupos:
            grupos = Grupo.objects.filter(cuentas__id = tarjeta.cuenta.id)
            if grupos.exists():
                saldo_anterior = TarjetaCredito.objects.get(id = tarjeta.id)
                saldo_anterior = saldo_anterior.saldo_inicial
                data = obtenerMonedas()
                for grupo in grupos:
                    grupo.balance -= cambiarMonedaJson(tarjeta.cuenta.tipo_moneda, grupo.tipo_moneda, saldo_anterior, data)
                    grupo.balance += cambiarMonedaJson(tarjeta.cuenta.tipo_moneda, grupo.tipo_moneda, tarjeta.saldo_inicial, data)
                    grupo.save()
        if commit:
            tarjeta.save()
        return tarjeta
        
    class Meta:
        model = TarjetaCredito
        fields = [
            'pasivos', 
            'limite',
            'cuota_manejo'
        ]



class PrestamoForm(forms.ModelForm):

    def save(self, commit=True):
        prestamo = super().save(commit=False)
        # do custom stuff
        
        TAE = self.cleaned_data["TAE"]
        montoNeto = self.cleaned_data["montoNeto"]
        mesesPago = self.cleaned_data["mesesPago"]
        interesNominal = 12*((TAE + 1.0)**(1/12) - 1)
        montoInteres = montoNeto + (montoNeto * interesNominal/100) * mesesPago/12
        prestamo.interesNominal = interesNominal
        prestamo.montoInteres = montoInteres
        prestamo.saldoPendiente = montoInteres
        prestamo.ultimoPago = date.today()
        prestamo.pagoMensual = round(montoInteres / mesesPago * 1.0, 2)
        if commit:
            prestamo.save()
        return prestamo


    def clean_TAE(self):
        TAE = self.cleaned_data.get('TAE')

        if TAE is not None and (TAE > 100 or TAE < 0):
            raise forms.ValidationError("La TAE debe ser un valor entre 0 y 100", code = "tae")
        return TAE
    
    def clean_mesesPago(self):
        mesesPago = self.cleaned_data.get('mesesPago')

        if mesesPago is not None and (mesesPago > 60 or mesesPago < 6):
            raise forms.ValidationError("El numero de meses en los que se paga debe estar entre 6 y 60", 
                                        code = "meses")
        return mesesPago

    class Meta:
        model = CuentaPrestamo
        fields = [
            'montoNeto', 
            'mesesPago',
            'TAE'
        ]


class AhorrosForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean ()
        saldo_inicial = cleaned_data.get("saldo_inicial")
        saldo_minimo_req = cleaned_data.get("saldo_minimo_req")
        
        if (saldo_inicial is not None and saldo_minimo_req is not None and
            saldo_inicial < saldo_minimo_req):
            
            msg = "El valor del saldo debe ser mayor al valor del saldo minimo requerido"
            self.add_error("saldo_minimo_req", msg)


    def save(self, commit = True, buscarGrupos = True):
        ahorros = super().save(commit=False)
        saldo_nuevo = self.cleaned_data["saldo_inicial"]
        if buscarGrupos:
            grupos = Grupo.objects.filter(cuentas__id = ahorros.cuenta.id)
            if grupos.exists():
                saldo_anterior = CuentaAhorros.objects.get(id = ahorros.id)
                saldo_anterior = saldo_anterior.saldo_inicial
                data = obtenerMonedas() 
                for grupo in grupos:
                    grupo.balance -= cambiarMonedaJson(ahorros.cuenta.tipo_moneda, grupo.tipo_moneda, saldo_anterior, data)
                    grupo.balance += cambiarMonedaJson(ahorros.cuenta.tipo_moneda, grupo.tipo_moneda, saldo_nuevo, data)
                    grupo.save()
        if commit: 
            ahorros.save()
        return ahorros


    class Meta:
        model = CuentaAhorros
        fields = [
            'saldo_inicial',
            'saldo_minimo_req'
        ]