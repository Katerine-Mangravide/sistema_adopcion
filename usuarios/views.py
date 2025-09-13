from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import RegistroForm, PerfilForm
from .models import Adoptante
from django.http import HttpResponse, JsonResponse
import json, csv
from mascotas.models import Mascota


def register_adoptante(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro exitoso. Revisa la consola para el email de confirmación (modo desarrollo).")
            return redirect('usuarios:login')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/register.html', {'form': form})

def login_adoptante(request):
    if request.method == "POST":
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('usuarios:home')
        messages.error(request, "Usuario o contraseña incorrectos / usuario inactivo.")
    return render(request, 'usuarios/login.html')

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
        form = PerfilForm(request.POST, request.FILES, instance=adoptante)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado.")
            return redirect('usuarios:perfil')
    else:
        form = PerfilForm(instance=adoptante)
    return render(request, 'usuarios/editar_perfil.html', {'form': form})

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
    if request.method == 'POST':
        adoptante = get_object_or_404(Adoptante, user=request.user)
        request.user.is_active = False
        request.user.save()
        adoptante.is_active = False
        adoptante.save()
        logout(request)
        messages.success(request, 'Cuenta desactivada.')
        return redirect('usuarios:login')
    return render(request, 'usuarios/confirmar_desactivar.html')

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
