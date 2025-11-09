from django.shortcuts import render, get_object_or_404, redirect
from .models import Seguimiento, Veterinario
from .forms import SeguimientoForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Veterinario
from .forms import VeterinarioForm
from usuarios.models import Refugio

def listar_seguimientos(request):
    seguimientos = Seguimiento.objects.select_related('mascota','veterinario').order_by('-fecha_revision','-hora_revision')
    return render(request, 'seguimiento/listar_seguimientos.html', {'seguimientos': seguimientos})

def agendar_revision(request):
    if request.method == 'POST':
        form = SeguimientoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('seguimiento:listar_seguimientos')
    else:
        form = SeguimientoForm()
    return render(request, 'seguimiento/agendar_revision.html', {'form': form})

def editar_seguimiento(request, pk):
    seguimiento = get_object_or_404(Seguimiento, pk=pk)
    if request.method == 'POST':
        form = SeguimientoForm(request.POST, instance=seguimiento)
        if form.is_valid():
            form.save()
            return redirect('seguimiento:listar_seguimientos')
    else:
        form = SeguimientoForm(instance=seguimiento)
    return render(request, 'seguimiento/editar_seguimiento.html', {'form': form, 'seguimiento': seguimiento})

def detalle_seguimiento(request, pk):
    seguimiento = get_object_or_404(Seguimiento, pk=pk)
    return render(request, 'seguimiento/detalle_seguimiento.html', {'seguimiento': seguimiento})

def registrar_seguimiento(request):
    if request.method == 'POST':
        form = SeguimientoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_seguimientos')
    else:
        form = SeguimientoForm()
    return render(request, 'seguimiento/registrar.html', {'form': form})

def listar_veterinarios_refugio(request):
    refugio = request.user.refugio
    veterinarios = Veterinario.objects.filter(refugio=refugio)
    return render(request, 'seguimiento/listar_veterinarios_refugio.html', {'veterinarios': veterinarios})


def es_refugio(user):
    if user.is_authenticated:
        try:
            return user.refugio.es_refugio
        except Refugio.DoesNotExist:
            return False
        except AttributeError:
            return False
    return False

@login_required
@user_passes_test(es_refugio)
def lista_veterinarios_refugio(request):
    refugio_usuario = request.user.refugio
    veterinarios = Veterinario.objects.filter(refugio=refugio_usuario)
    return render(request, 'seguimiento/lista_veterinarios.html', {'veterinarios': veterinarios, 'refugio': refugio_usuario})

@login_required
@user_passes_test(es_refugio)
def agregar_veterinario_refugio(request):
    refugio_usuario = request.user.refugio
    if request.method == 'POST':
        form = VeterinarioForm(request.POST)
        if form.is_valid():
            veterinario = form.save(commit=False)
            veterinario.refugio = refugio_usuario
            veterinario.save()
            messages.success(request, f"Veterinario '{veterinario.nombre}' agregado correctamente.")
            return redirect('seguimiento:lista_veterinarios_refugio')
    else:
        form = VeterinarioForm()
    return render(request, 'seguimiento/agregar_veterinario.html', {'form': form})

@login_required
@user_passes_test(es_refugio)
def editar_veterinario_refugio(request, pk):
    refugio_usuario = request.user.refugio
    veterinario = get_object_or_404(Veterinario, pk=pk, refugio=refugio_usuario)
    if request.method == 'POST':
        form = VeterinarioForm(request.POST, instance=veterinario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Veterinario '{veterinario.nombre}' actualizado correctamente.")
            return redirect('seguimiento:lista_veterinarios_refugio')
    else:
        form = VeterinarioForm(instance=veterinario)
    return render(request, 'seguimiento/editar_veterinario.html', {'form': form, 'veterinario': veterinario})

@login_required
@user_passes_test(es_refugio)
def eliminar_veterinario_refugio(request, pk):
    refugio_usuario = request.user.refugio
    veterinario = get_object_or_404(Veterinario, pk=pk, refugio=refugio_usuario)
    nombre = veterinario.nombre
    veterinario.delete()
    messages.success(request, f"Veterinario '{nombre}' eliminado correctamente.")
    return redirect('seguimiento:lista_veterinarios_refugio')

@login_required
@user_passes_test(es_refugio)
def agendar_revision(request):
    refugio = request.user.refugio
    if request.method == 'POST':
        form = SeguimientoForm(request.POST, refugio=refugio)
        if form.is_valid():
            form.save()
            return redirect('seguimiento:listar_seguimientos')
    else:
        form = SeguimientoForm(refugio=refugio)

    return render(request, 'seguimiento/agendar_revision.html', {'form': form})



