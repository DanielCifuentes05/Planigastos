from django import forms
from datetime import datetime
from django.utils import formats
from .models import Presupuesto
from cuenta.models import CuentaGenerica
from usuario.models import Usuario, User
from django.forms.models import ModelMultipleChoiceField
from django.core.mail import send_mail

class PresupuestoForm(forms.ModelForm):
    recurrencia = forms.BooleanField(required=False)
    cuentas = forms.ModelMultipleChoiceField( widget = forms.CheckboxSelectMultiple, queryset = CuentaGenerica.objects.all() ,
                                            required= True)

    class Meta():
        model= Presupuesto
        fields = [
            'nombre',
            'duracion',
            'icono',
            'recurrencia',
            'saldoTotal',
            'tipo_moneda'
        ]


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('usuario')
    
        super().__init__(*args, **kwargs)
        self.usuario = Usuario.objects.get(usuariodjango = self.user)
        self.fields['cuentas'].queryset = CuentaGenerica.objects.filter(usuario=self.usuario)


    def save(self, commit=True):
        
        presupuesto = super().save(commit=False)
        date_joined = datetime.now().date()
        # do custom stuff
        presupuesto.usuario = self.usuario
        presupuesto.saldoConsumido = 0
        presupuesto.fechaInicio = date_joined
        cuentas = self.cleaned_data["cuentas"]
        if commit:
            presupuesto.save()
        for cuenta in cuentas:
            presupuesto.cuentas.add(cuenta)
        return presupuesto



def enviarMail(presupuesto, id_cuenta):
    if presupuesto.saldoConsumido/presupuesto.saldoTotal > 1:
        usuario = User.objects.get(id = id_cuenta)
        mssg = ("Hola " + usuario.first_name + " " + usuario.last_name +  
                "tu presupuesto " + presupuesto.nombre + " se ha acabado")
        send_mail(
            '¡Saldo de presupuesto agotado!',
            mssg,
            'planigastos@gmail.com',
            [usuario.email],
        )
    elif presupuesto.saldoConsumido/presupuesto.saldoTotal > 0.6:
        usuario = User.objects.get(id = id_cuenta)
        mssg = ("Hola " + usuario.first_name + " " + usuario.last_name +  
                "tu presupuesto " + presupuesto.nombre + " está a punto de acabarse (" + 
                str(round(presupuesto.saldoConsumido*100/presupuesto.saldoTotal, 2)) + "%)")
        send_mail(
            'Saldo de presupuesto a punto de acabarse',
            mssg,
            'planigastos@gmail.com',
            [usuario.email],
        )



class PresupuestoForm2(forms.ModelForm):
    recurrencia = forms.BooleanField(required=False)
    cuentas = forms.ModelMultipleChoiceField( widget = forms.CheckboxSelectMultiple, queryset = CuentaGenerica.objects.all() ,
                                            required= False)

    class Meta():
        model= Presupuesto
        fields = [
            'nombre',
            'duracion',
            'icono',
            'recurrencia',
            'saldoTotal',
            'tipo_moneda'
        ]


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('usuario')
        self.presupuesto = kwargs.pop('presupuesto')
        super().__init__(*args, **kwargs)
        self.usuario = Usuario.objects.get(usuariodjango = self.user)
        self.fields['cuentas'].queryset = CuentaGenerica.objects.filter(usuario=self.usuario).exclude(presupuesto__id = self.presupuesto)


    def save(self, commit=True):
        
        presupuesto = super().save(commit=False)
        date_joined = datetime.now().date()
        # do custom stuff
        presupuesto.usuario = self.usuario
        presupuesto.fechaInicio = date_joined
        cuentas = self.cleaned_data["cuentas"]
        if commit:
            presupuesto.save()
        for cuenta in cuentas:
            presupuesto.cuentas.add(cuenta)

        enviarMail(presupuesto, self.usuario.usuariodjango.id)
        return presupuesto
        
