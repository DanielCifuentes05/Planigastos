from django import forms 
from .models import Usuario
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.functions import ExtractYear
import re 

class CrearUsuarioForm(forms.ModelForm):

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get("fecha_nacimiento")
        year = int(fecha_nacimiento.strftime('%Y'))
        if 2019 - year < 18:
            raise forms.ValidationError("Solo se pueden registrar personas mayores de edad", 
                                        code = "edad")
        elif 2019 - year > 110:
            raise forms.ValidationError("No puedes tener mas de 110 anios", 
                                        code = "edad")
        return fecha_nacimiento


    def clean_cedula(self):
        cedula = self.cleaned_data.get("cedula")
        if cedula is not None:
           if len(str((cedula))) < 7 or len(str(cedula)) > 11:
               raise forms.ValidationError("La cedula debe tener entre 7 y 11 digitos", code = "cedula")
        return cedula 

    class Meta:
        model = Usuario 
        fields = [
            'fecha_nacimiento',
            'cedula'
        ]
        labels = {
            'fecha_nacimiento' : 'Fecha de Nacimiento',
            'cedula'  : 'Cedula'
        }
        widgets = {
            'fecha_nacimiento' : forms.DateInput(),
            'cedula' : forms.NumberInput(),
        }

class RegistroForm(UserCreationForm):

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        numeros = "0123456789!#$%&/()='¿[]}{"

        res = any(i in first_name for i in numeros) 
        if res:
            raise forms.ValidationError("El nombre no puede tener numeros o simbolos", code = "nombre")
        if len(first_name) == 0:
             raise forms.ValidationError("El nombre no puede estar vacío o solo con espacios", code = "nombre")
        x = re.match(r"((\S)*?(\s){2,}(\S)*?)+", first_name)
        if x:
            raise forms.ValidationError("El nombre no puede tener dos o mas espacios seguidos", code = "nombre")
        return first_name

    
    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        numeros = "0123456789!#$%&/()='¿[]}{"

        res = any(i in last_name for i in numeros) 
        if res:
            raise forms.ValidationError("El nombre no puede tener numeros o simbolos", code = "apellido")

        if len(last_name) == 0:
             raise forms.ValidationError("El apellido no puede estar vacío o solo con espacios", code = "apellido")
        x = re.match(r"((\S)*?(\s){2,}(\S)*?)+", last_name)
        if x:
            raise forms.ValidationError("El apellido no puede tener dos o mas espacios seguidos", code = "apellido")
        return last_name

    def clean_email(self):
       email = self.cleaned_data.get('email')
       if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta asociada a este correo electronico", code = "email")
       return email

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]

        labels = {
            'username' : "Nombre de Usuario",
            'first_name' : "Primer Nombre",
            'last_name': "Apellido",
            'email' : "Correo electronico",
        }

        widgets = {
            'username' : forms.TextInput(attrs={'class' : 'form-control',
                                              'placeholder' : 'Digita tu nombre de usuario'}),
            'first_name' : forms.TextInput(attrs={'class' : 'form-control',
                                              'placeholder' : 'Digita tu primer nombre'}),
            'last_name' : forms.TextInput(attrs={'class' : 'form-control',
                                              'placeholder' : 'Digita tu apellido'}),
            'email' : forms.EmailInput(attrs={'class' : 'form-control',
                                              'placeholder' : 'Digita tu correo'}),                                                            
        }


class ValidateEspacios(object):
    def validate(self, password, user=None):
        if re.match(r"((\S)*?(\s){2,}(\S)*?)+", password):
            raise forms.ValidationError(
                "La contraseña no puede ser solo espacios o tener dos o mas espacios seguidos",
                code='password_espacios',
            )
    
    
    def get_help_text(self):
        return "Tu password no debe tener mas dos o mas espacios seguidos y no debe ser solo espacios"
    