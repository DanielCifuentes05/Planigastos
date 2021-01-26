from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Usuario(models.Model):
    usuariodjango = models.OneToOneField(User, on_delete = models.CASCADE)

    fecha_nacimiento = models.DateField()
    cedula = models.IntegerField(unique=True)


    def __str__(self):
        return f'{self.usuariodjango.username} {self.usuariodjango.first_name} {self.usuariodjango.last_name}'