from django import forms
from .models import Grupo
from usuario.models import Usuario
from cuenta.models import *
from django.forms.models import ModelMultipleChoiceField
from planigastos.convertirMoneda import *
import re


def actualizarBalance(grupo, cuentas):
        id_cuentas_grupo = [cuenta.id for cuenta in grupo.cuentas.all()]
        jsonMoneda = obtenerMonedas()
        saldo_inicial = 0
        print("CUENTAS", id_cuentas_grupo)
        for id_cuenta in id_cuentas_grupo:
            cuenta_especifica = None
            print("\tBUSCANDO QUERY DE ", id_cuenta)
            if CuentaEfectivo.objects.filter(cuenta_id = id_cuenta).exists():
                cuenta_especifica = CuentaEfectivo.objects.get(cuenta_id = id_cuenta)
                print("EFECTIVO")
            elif TarjetaCredito.objects.filter(cuenta_id = id_cuenta).exists():
                cuenta_especifica = TarjetaCredito.objects.get(cuenta_id = id_cuenta)
                print("TARJETA")
            elif CuentaAhorros.objects.filter(cuenta_id = id_cuenta).exists():
                print("AHORROS")
                cuenta_especifica = CuentaAhorros.objects.get(cuenta_id = id_cuenta)
            
            saldo_inicial += cambiarMonedaJson(cuenta_especifica.cuenta.tipo_moneda, grupo.tipo_moneda, 
                                                cuenta_especifica.saldo_inicial, jsonMoneda)
            print("SALDO INICIAL DE LA CUENTA", saldo_inicial)
        
        grupo.balance = saldo_inicial
        grupo.save()


class CrearGrupoForm(forms.ModelForm):
    cuentas = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                queryset = CuentaGenerica.objects.all(), #Igual este queryset se actualiza
                required=True)

    #Se sobreescribe el metodo init para que se muestren solo las cuentas
    #del usuario que esta autenticado
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('usuario')
    
        super(CrearGrupoForm, self).__init__(*args, **kwargs)
        self.usuario = Usuario.objects.get(usuariodjango = self.user)
        prestamos = (CuentaPrestamo.objects.all())
        id_prestamos = [prestamo.cuenta.id for prestamo in prestamos]
        self.fields['cuentas'].queryset = CuentaGenerica.objects.filter(usuario=self.usuario).exclude(id__in = id_prestamos)
        
    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if len(nombre) == 0:
             raise forms.ValidationError("El nombre no puede estar vacío o solo con espacios", code = "nombre")
        x = re.match(r"((\S)*?(\s){2,}(\S)*?)+", nombre)
        #print(x)
        if x:
            raise forms.ValidationError("El nombre no puede tener dos o mas espacios seguidos", code = "nombre")
        return nombre

    def save(self, commit=True):
        grupo = super().save(commit=False)
        print("SAVE")
        # do custom stuff
        grupo.usuario = self.usuario
        cuentas = self.cleaned_data["cuentas"]

        if commit:
            grupo.save()

        for cuenta in cuentas:
            grupo.cuentas.add(cuenta)
        actualizarBalance(grupo, cuentas)
        return grupo


    class Meta:
        model = Grupo
        fields = [
            'nombre', 
            'cuentas',
            'icono', 
            'tipo_moneda'
        ]

        
class CrearGrupoForm2(forms.ModelForm):
    cuentas = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                queryset = CuentaGenerica.objects.all(), #Igual este queryset se actualiza
                required=False)

    #Se sobreescribe el metodo init para que se muestren solo las cuentas
    #del usuario que esta autenticado
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('usuario')
        self.grupo = kwargs.pop('grupo')
        super(CrearGrupoForm2, self).__init__(*args, **kwargs)
        self.usuario = Usuario.objects.get(usuariodjango = self.user)

        cuentasSinGrupo = (CuentaGenerica.objects.filter(usuario = self.usuario)).exclude(grupo__id = self.grupo)
        
        self.fields['cuentas'].queryset = cuentasSinGrupo

    

    def save(self, commit=True):
        grupo = super(CrearGrupoForm2, self).save(commit=False)
        # do custom stuff
        grupo.usuario = self.usuario
        cuentas = self.cleaned_data["cuentas"]
        if commit:
            grupo.save()
        for cuenta in cuentas:
            grupo.cuentas.add(cuenta)

        actualizarBalance(grupo, cuentas)
        return grupo

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
        model = Grupo
        fields = [
            'nombre', 
            'cuentas',
            'icono'
        ]