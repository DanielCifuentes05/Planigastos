from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import CreateView

from .models import Usuario
from .forms import RegistroForm, CrearUsuarioForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.views.generic import TemplateView, DetailView, UpdateView
from django.template.context import RequestContext
# Create your views here.


class VerUsuario(DetailView):
    model = Usuario
    template_name = "user/verUsuario.html"
    
class ModificarUsuario(UpdateView):
    model = Usuario
    template_name = 'user/modificarUsuario.html'
    form_class = CrearUsuarioForm
    second_form_class = RegistroForm

    def get_success_url(self):
        return reverse_lazy("usuario:verPerfil", kwargs = {'pk' : self.kwargs.get("pk")})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = get_object_or_404(Usuario, pk=self.kwargs.get("pk"))
        if 'form' not in context:
            context['form'] = self.form_class(instance=usuario)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(instance=usuario.usuariodjango)
        return context

class CrearUsuario(CreateView):
    model = Usuario
    template_name = 'user/crearUsuario.html'
    form_class = CrearUsuarioForm
    second_form_class = RegistroForm
    success_url = reverse_lazy("usuario:login")


    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST)
        if form.is_valid() and form2.is_valid():
            usuario = form.save(commit = False)
            usuario.usuariodjango = form2.save()
            usuario.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(request, self.template_name, 
                                        context = {'form': form, 'form2':form2})
            

class LoginUsuario(LoginView):
    template_name = "user/login.html"

    def get_success_url(self):
        return reverse_lazy("usuario:cuentaInicio")

class Inicio(TemplateView):
    template_name = "user/cuentaInicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = Usuario.objects.get(usuariodjango_id = self.request.user)
        print("USUARIO", usuario)
        context['usuario'] = usuario
        return context

class Landing(TemplateView):
    template_name = "inicio.html"


class CambiarPass(PasswordChangeView):
    template_name = "user/cambiarPass.html"
    
    
    def get_success_url(self):
        id_usuario = Usuario.objects.get(usuariodjango_id = (self.request.user).id).id
        return reverse_lazy("usuario:verPerfil", kwargs = {'pk' : id_usuario})