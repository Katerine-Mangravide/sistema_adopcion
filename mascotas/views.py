# mascotas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Mascota, SolicitudAdopcion, Refugio
from .forms import SolicitudAdopcionForm, EstadoSolicitudForm, MascotaForm
from usuarios.models import Adoptante
from django.contrib.auth.decorators import user_passes_test
from usuarios.models import Refugio
from django import forms
from django.views.decorators.http import require_http_methods


@login_required
def solicitar_adopcion(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)

    # obtener el adoptante logueado
    adoptante = get_object_or_404(Adoptante, user=request.user)

    # verificar si ya hizo una solicitud para esa mascota
    if SolicitudAdopcion.objects.filter(mascota=mascota, email=adoptante.user.email).exists():
        messages.warning(request, "Ya has enviado una solicitud para esta mascota.")
        return redirect('mascotas:detalle_mascota', mascota_id=mascota.id)

    if request.method == "POST":
        form = SolicitudAdopcionForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.mascota = mascota
            solicitud.nombre_adoptante = adoptante.user.first_name
            solicitud.apellido_adoptante = adoptante.user.last_name
            solicitud.telefono = form.cleaned_data['telefono']
            solicitud.email = adoptante.user.email
            solicitud.direccion = form.cleaned_data['direccion']
            solicitud.save()
            messages.success(request, "Tu solicitud de adopción fue enviada con éxito.")
            return redirect('usuarios:solicitud_enviada')
    else:
        form = SolicitudAdopcionForm(initial={'telefono': adoptante.telefono, 'direccion': adoptante.direccion})
        

    return render(request, 'mascotas/solicitar_adopcion.html', {'form': form, 'mascota': mascota, 'adoptante': adoptante})

def detalle_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    
    context = {
        'mascota': mascota,
    }
    return render(request, 'mascotas/detalle_mascota.html', context)

def es_refugio(user):
    """Verifica si el usuario logueado está asociado a un perfil Refugio."""
    if user.is_authenticated:
        try:
            # Accede al perfil Refugio del usuario y verifica el campo
            return user.refugio.es_refugio
        except Refugio.DoesNotExist:
            return False
        except AttributeError:
            return False
    return False

@login_required
@user_passes_test(es_refugio, login_url='/usuarios/login/')
def lista_mascotas_refugio(request):
    """
    Muestra la lista de mascotas que pertenecen al refugio del usuario logueado.
    """
    refugio_usuario = request.user.refugio
    
    # Filtra de forma SEGURA solo las mascotas de este refugio
    mascotas = Mascota.objects.filter(refugio=refugio_usuario).order_by('-fecha_ingreso')
    
    contexto = {
        'mascotas': mascotas,
        'refugio': refugio_usuario
    }
    return render(request, 'mascotas/lista_mascotas_refugio.html', contexto)

@login_required
@user_passes_test(es_refugio, login_url='/usuarios/login/')
def agregar_mascota_refugio(request):
    refugio_usuario = request.user.refugio
    
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            mascota = form.save(commit=False)
            mascota.refugio = refugio_usuario  # Asignar el refugio automáticamente
            mascota.save()
            messages.success(request, f"La mascota '{mascota.nombre}' ha sido registrada con éxito.")
            return redirect('mascotas:lista_mascotas_refugio')
    else:
        form = MascotaForm()

    contexto = {
        'form': form,
    }
    return render(request, 'mascotas/agregar_mascota.html', contexto)

@login_required
@user_passes_test(es_refugio, login_url='/usuarios/login/')
def editar_mascota(request, pk):
    refugio_usuario = request.user.refugio
    
    # CLAVE DE SEGURIDAD: Solo permite editar mascotas del refugio del usuario
    mascota = get_object_or_404(Mascota, pk=pk, refugio=refugio_usuario)
    
    if request.method == 'POST':
        # Nota: Usamos request.FILES para la imagen, e instance=mascota para editar
        form = MascotaForm(request.POST, request.FILES, instance=mascota) 
        if form.is_valid():
            form.save()
            messages.success(request, f"La mascota '{mascota.nombre}' ha sido actualizada correctamente.")
            return redirect('mascotas:lista_mascotas_refugio')
    else:
        form = MascotaForm(instance=mascota)

    contexto = {
        'form': form,
        'mascota': mascota
    }
    return render(request, 'mascotas/editar_mascota.html', contexto)

@login_required
@user_passes_test(es_refugio, login_url='/usuarios/login/')
def gestion_solicitudes_refugio(request):
    refugio_usuario = request.user.refugio
    
    # 1. Obtener IDs de las mascotas que pertenecen al refugio logueado
    mascota_ids = Mascota.objects.filter(refugio=refugio_usuario).values_list('id', flat=True)
    
    # 2. Filtrar Solicitudes: obtener todas las solicitudes hechas para esas mascotas
    solicitudes = SolicitudAdopcion.objects.filter(
        mascota__id__in=mascota_ids 
    ).select_related('mascota').order_by('-fecha_solicitud')
    
    contexto = {
        'solicitudes': solicitudes,
        'refugio_nombre': refugio_usuario.nombre
    }
    return render(request, 'mascotas/gestion_solicitudes_refugio.html', contexto)


@login_required
@user_passes_test(es_refugio, login_url='/usuarios/login/')
def detalle_solicitud_refugio(request, pk):
    refugio_usuario = request.user.refugio
    
    # CLAVE DE SEGURIDAD: Solo permite acceder a solicitudes de sus propias mascotas
    solicitud = get_object_or_404(
        SolicitudAdopcion.objects.select_related('mascota'), 
        pk=pk, 
        mascota__refugio=refugio_usuario
    )

    if request.method == "POST":
        form = EstadoSolicitudForm(request.POST, instance=solicitud)
        if form.is_valid():
            nueva_solicitud = form.save()
            
            # Lógica extra al aprobar: si se aprueba, marca la mascota como adoptada
            if nueva_solicitud.estado == 'aprobada':
                mascota = nueva_solicitud.mascota
                mascota.adoptada = True
                mascota.save()
            
            messages.success(request, f"Estado de la solicitud de {solicitud.nombre_adoptante} actualizado a '{nueva_solicitud.get_estado_display()}'")
            return redirect('mascotas:gestion_solicitudes_refugio')
    else:
        form = EstadoSolicitudForm(instance=solicitud)

    contexto = {
        'solicitud': solicitud,
        'form': form
    }
    return render(request, 'mascotas/detalle_solicitud_refugio.html', contexto)

@require_http_methods(["POST"]) # Solo permite acceso vía POST
@login_required
@user_passes_test(es_refugio, login_url='/usuarios/login/')
def eliminar_mascota(request, pk):
    refugio_usuario = request.user.refugio
    
    # CLAVE DE SEGURIDAD: Solo permite eliminar si la mascota pertenece al refugio del usuario
    mascota = get_object_or_404(Mascota, pk=pk, refugio=refugio_usuario)
    
    nombre_mascota = mascota.nombre
    mascota.delete()
    
    messages.success(request, f"La mascota '{nombre_mascota}' ha sido eliminada correctamente.")
    return redirect('mascotas:lista_mascotas_refugio')