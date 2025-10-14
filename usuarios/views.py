from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.db import transaction
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
import json, csv
from .forms import RegistroForm, UserForm, AdoptanteForm, RegistroRefugioForm, RefugioForm 
from .models import Adoptante, Refugio
from mascotas.models import Mascota, SolicitudAdopcion
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test

def register_adoptante(request):
    if request.method == "POST":
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            # crear usuario
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
                email=form.cleaned_data.get('email', ''),
            )
            adoptante = form.save(commit=False)
            adoptante.user = user
            adoptante.save()
            login(request, user)
            messages.success(request, "Registro exitoso. Bienvenido/a.")
            return redirect('usuarios:perfil')
    else:
        form = RegistroForm()
    return render(request, "usuarios/register.html", {"form": form})

def register_refugio(request):
    if request.method == "POST":
        form = RegistroRefugioForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Crear el objeto User
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data.get('first_name', ''),
                        last_name=form.cleaned_data.get('last_name', ''),
                        email=form.cleaned_data.get('email', ''),
                    )
                    # 2. Crear el objeto Refugio, vinculado al User
                    refugio = form.save(commit=False)
                    refugio.usuario = user
                    refugio.es_refugio = True # Importante para la lógica de permisos
                    refugio.save()

                    login(request, user)
                    messages.success(request, f"Refugio {refugio.nombre} registrado. Bienvenido/a al panel.")
                    # Redirigimos al panel del refugio
                    return redirect('usuarios:panel_refugio')

            except Exception as e:
                # Manejo simple de errores (ej. si falla la transacción)
                messages.error(request, f"Ocurrió un error en el registro: {e}")
                
    else:
        form = RegistroRefugioForm()
        
    return render(request, "usuarios/register_refugio.html", {"form": form})

# usuarios/views.py (función login_adoptante)

def login_adoptante(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user and user.is_active:
                login(request, user)
                messages.success(request, "Has iniciado sesión correctamente.")

                # 🔑 LÓGICA DE REDIRECCIÓN CONDICIONAL APLICADA AQUÍ
                
                # 1. Redireccionar al Refugio/Admin (is_staff=True)
                if user.is_staff:
                    try:
                        # Si es staff y tiene un perfil de Refugio, va al panel de Refugio
                        if hasattr(user, 'refugio'):
                            # ✅ ESTA DEBERÍA SER LA URL DEL PANEL DE REFUGIO
                            return redirect('usuarios:panel_refugio') 
                        else:
                            # Si es staff pero no tiene perfil de Refugio (Superadmin puro)
                            return redirect('admin_panel:dashboard')
                    except Exception:
                        # Fallback por si el objeto 'refugio' no está bien cargado o mapeado
                        return redirect('admin_panel:dashboard')

                # 2. Redireccionar al Adoptante (por defecto)
                else:
                    # El adoptante va a su perfil
                    return redirect('usuarios:perfil') 
                    
            else:
                messages.error(request, "Cuenta inactiva.")
    else:
        form = AuthenticationForm()
        
    # Manejar el parámetro 'next' si existe (ej. si se intentó acceder a una página protegida)
    next_url = request.GET.get('next')
    if next_url:
        return render(request, 'usuarios/login.html', {'form': form, 'next': next_url})
        
    return render(request, 'usuarios/login.html', {'form': form})



def logout_adoptante(request):
    # esperamos POST para cerrar sesión desde el formulario del header
    if request.method == "POST":
        logout(request)
        # 👇 Dejamos SOLO este mensaje (el template logout.html ya no debería tener mensaje fijo)
        messages.success(request, "Sesión cerrada correctamente.")
        return redirect('usuarios:login')
    # si alguien intenta GET, lo llevamos a home
    return redirect('usuarios:home')


def home(request):
    qs = Mascota.objects.filter(adoptada=False)

    q = request.GET.get('q', '').strip()
    especie = request.GET.get('especie', '').strip()
    raza = request.GET.get('raza', '').strip()
    ciudad = request.GET.get('ciudad', '').strip()

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(raza__icontains=q) | Q(especie__icontains=q))
    if especie:
        qs = qs.filter(especie__iexact=especie)
    if raza:
        qs = qs.filter(raza__iexact=raza)
    if ciudad:
        qs = qs.filter(refugio__direccion__icontains=ciudad)

    especies = Mascota.objects.order_by().values_list('especie', flat=True).distinct()
    razas = Mascota.objects.order_by().values_list('raza', flat=True).exclude(raza__exact='').distinct()
    # Ciudades (Mejor obtenidas desde Refugio)
    ciudades = (Refugio.objects
                .order_by() 
                .values_list('direccion', flat=True)
                .exclude(direccion__exact='')
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
    # 🔑 CORRECCIÓN: Si el usuario tiene un perfil de Refugio, redirigir allí.
    try:
        if request.user.refugio.es_refugio:
            return redirect('usuarios:panel_refugio')
    except Refugio.DoesNotExist:
        # Esto significa que el usuario NO es un Refugio, que es lo esperado para un Adoptante.
        pass
    except AttributeError:
        # Maneja casos donde 'user.refugio' no existe
        pass

    # Lógica original para Adoptantes:
    adoptante = get_object_or_404(Adoptante, user=request.user)
    return render(request, 'usuarios/perfil.html', {'adoptante': adoptante})


@login_required
def editar_perfil(request):
    adoptante = get_object_or_404(Adoptante, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        adoptante_form = AdoptanteForm(request.POST, request.FILES, instance=adoptante)
        if user_form.is_valid() and adoptante_form.is_valid():
            user_form.save()
            adoptante_form.save()
            messages.success(request, "Perfil actualizado.")
            return redirect('usuarios:perfil')
        else:
            messages.error(request, "Corrige los errores del formulario.")
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
            messages.error(request, 'Corrige los errores.')
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
    
    # Vista para el panel de administración web
@staff_member_required(login_url='usuarios:login')
def admin_dashboard(request):
    """
    Dashboard para el administrador.
    Redirige a la vista de administración de Django, pero puede extenderse
    para mostrar estadísticas, links directos a modelos, etc.
    """
    return render(request, 'usuarios/admin_dashboard.html')

def es_refugio(user):
    """Verifica si el usuario logueado está asociado a un perfil Refugio."""
    try:
        # Devuelve True si el perfil Refugio existe y tiene el campo es_refugio=True
        return user.refugio.es_refugio
    except Refugio.DoesNotExist:
        return False
    except AttributeError:
        # Maneja el caso en que user.refugio no existe (es Adoptante o Admin)
        return False


@user_passes_test(es_refugio, login_url='usuarios:login')
@login_required
def panel_refugio(request):
    # Accede directamente al objeto Refugio a través del usuario logueado
    refugio_usuario = request.user.refugio
    
    # 1. Mascotas propias: Filtra todas las mascotas que le pertenecen
    mascotas_propias = Mascota.objects.filter(refugio=refugio_usuario).order_by('-fecha_ingreso')
    
    # 2. Solicitudes pendientes: Filtra solicitudes de SUS mascotas en estado 'pendiente'
    solicitudes_pendientes = SolicitudAdopcion.objects.filter(
        mascota__in=mascotas_propias, # Filtra por las mascotas que acabamos de obtener
        estado='pendiente'
    ).select_related('mascota').order_by('-fecha_solicitud')
    
    contexto = {
        'refugio': refugio_usuario,
        'mascotas_propias': mascotas_propias,
        'solicitudes_pendientes': solicitudes_pendientes,
        'conteo_mascotas': mascotas_propias.count(),
        'conteo_solicitudes': solicitudes_pendientes.count(),
    }
    return render(request, 'usuarios/panel_refugio.html', contexto)

@user_passes_test(es_refugio, login_url='usuarios:login')
@login_required
def editar_perfil_refugio(request):
    """Permite a un usuario de tipo Refugio editar su perfil y la info del User asociado."""
    
    try:
        refugio = request.user.refugio
    except Refugio.DoesNotExist:
        messages.error(request, 'Error: Tu perfil de refugio no está vinculado correctamente.')
        return redirect('usuarios:panel_refugio')

    if request.method == "POST":
        # UserForm: maneja first_name, last_name, email (del User)
        user_form = UserForm(request.POST, instance=request.user)
        
        # RefugioForm: maneja nombre, direccion, telefono (del Refugio)
        refugio_form = RefugioForm(request.POST, instance=refugio) # <-- USAMOS RefugioForm
        
        if user_form.is_valid() and refugio_form.is_valid():
            user_form.save()
            refugio_form.save()
            messages.success(request, "Los datos de tu Refugio han sido actualizados con éxito.")
            return redirect('usuarios:panel_refugio')
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        user_form = UserForm(instance=request.user)
        refugio_form = RefugioForm(instance=refugio) # <-- USAMOS RefugioForm

    return render(request, 'usuarios/editar_perfil_refugio.html', {
        'user_form': user_form,
        'refugio_form': refugio_form
    })

@login_required
def solicitud_enviada(request):
    return render(request, 'usuarios/solicitud_enviada.html')

@login_required
def mis_solicitudes(request):
    # Obtiene todas las solicitudes hechas por el email del usuario logueado
    solicitudes = SolicitudAdopcion.objects.filter(email=request.user.email).order_by('-fecha_solicitud')

    contexto = {'solicitudes': solicitudes}
    return render(request, 'usuarios/mis_solicitudes.html', contexto)

    # usuarios/views.py

# ... otras vistas (panel_refugio, editar_perfil_refugio, etc.)

# 🔑 NUEVA VISTA: GESTIÓN DE REDIRECCIÓN DESPUÉS DEL LOGIN