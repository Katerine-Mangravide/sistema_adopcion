from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import RegistroForm, PerfilForm
from django.http import HttpResponse, JsonResponse
import json, csv
from mascotas.models import Mascota
from .forms import UserForm, AdoptanteForm
from .models import Adoptante
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


def register_adoptante(request):
    if request.method == "POST":
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
            )
            adoptante = form.save(commit=False)
            adoptante.user = user
            adoptante.save()
            login(request, user)  # inicia sesión automáticamente
            return redirect('usuarios:home')
    else:
        form = RegistroForm()

    return render(request, "usuarios/register.html", {"form": form})

def login_adoptante(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('usuarios:home')
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {"form": form})

def logout_adoptante(request):
    logout(request)
    messages.success(request, "Sesión cerrada.")
    return redirect('usuarios:login')

def home(request):
    qs = Mascota.objects.filter(adoptada=False)  # solo no adoptadas

    q = request.GET.get('q', '').strip()
    especie = request.GET.get('especie', '').strip()
    raza = request.GET.get('raza', '').strip()
    ciudad = request.GET.get('ciudad', '').strip()

    # Buscar por nombre o raza
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(raza__icontains=q))

    if especie:
        qs = qs.filter(especie__iexact=especie)
    if raza:
        qs = qs.filter(raza__iexact=raza)
    if ciudad:
        qs = qs.filter(refugio__direccion__icontains=ciudad)

    # Opciones dinámicas
    especies = Mascota.objects.values_list('especie', flat=True).distinct()
    razas = Mascota.objects.values_list('raza', flat=True).exclude(raza__exact='').distinct()
    ciudades = (Mascota.objects.values_list('refugio__direccion', flat=True)
                .exclude(refugio__direccion__exact='')
                .distinct())

    context = {
        'mascotas': qs,
        'especies': especies,
        'razas': razas,
        'ciudades': ciudades,
    }
    return render(request, 'usuarios/home.html', context)

@login_required
def ver_perfil(request):
    adoptante = get_object_or_404(Adoptante, user=request.user)
    return render(request, 'usuarios/perfil.html', {'adoptante': adoptante})

@login_required
def editar_perfil(request):
    adoptante = get_object_or_404(Adoptante, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        adoptante_form = AdoptanteForm(request.POST, instance=adoptante)
        if user_form.is_valid() and adoptante_form.is_valid():
            user_form.save()
            adoptante_form.save()
            return redirect('usuarios:perfil')
    else:
        user_form = UserForm(instance=request.user)
        adoptante_form = AdoptanteForm(instance=adoptante)

    return render(request, 'usuarios/editar_perfil.html', {
        'user_form': user_form,
        'adoptante_form': adoptante_form
    })

@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada.')
            return redirect('usuarios:perfil')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'usuarios/cambiar_contrasena.html', {'form': form})

@login_required
def desactivar_cuenta(request):
    adoptante = get_object_or_404(Adoptante, user=request.user)

    if request.method == "POST":
        adoptante.is_active = False
        adoptante.save()
        request.user.is_active = False
        request.user.save()

        logout(request)
        messages.success(request, "Tu cuenta ha sido desactivada correctamente.")
        return redirect("usuarios:home")

    return render(request, "usuarios/desactivar_cuenta.html")

@login_required
def descargar_datos(request, formato='json'):
    adoptante = get_object_or_404(Adoptante, user=request.user)
    data = {
        'nombre': request.user.first_name,
        'apellido': request.user.last_name,
        'cedula': adoptante.cedula,
        'email': request.user.email,
        'telefono': adoptante.telefono,
        'direccion': adoptante.direccion,
        'fecha_registro': adoptante.fecha_registro.isoformat(),
    }
    if formato == 'json':
        response = HttpResponse(json.dumps(data, ensure_ascii=False, indent=2), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename=datos_{request.user.username}.json'
        return response
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=datos_{request.user.username}.csv'
        writer = csv.writer(response)
        writer.writerow(data.keys())
        writer.writerow(data.values())
        return response
