from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
from usuarios.forms import UserForm, AdoptanteForm
from usuarios.models import Adoptante
from mascotas.models import Mascota, Refugio, SolicitudAdopcion
from .forms import CrearUsuarioForm, EditarUsuarioForm, EditarUserForm, RefugioForm, MascotaForm, SolicitudForm, SolicitudAdminForm, CrearRefugioUserForm # <-- ¡Añade esto!


# Decorator: solo staff (admin)
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='usuarios:login')(view_func)


# ---------- DASHBOARD ----------
@admin_required
def dashboard(request):
    total_usuarios = Adoptante.objects.count()
    total_mascotas = Mascota.objects.count()
    total_refugios = Refugio.objects.count()
    total_solicitudes = SolicitudAdopcion.objects.count()

    context = {
        'total_usuarios': total_usuarios,
        'total_mascotas': total_mascotas,
        'total_refugios': total_refugios,
        'total_solicitudes': total_solicitudes,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ---------- USUARIOS ----------
@admin_required
def gestion_usuarios(request):
    adoptantes = Adoptante.objects.select_related('user').all()
    return render(request, 'admin_panel/usuarios.html', {'adoptantes': adoptantes})

@admin_required
def crear_usuario(request):
    if request.method == "POST":
        form = CrearUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            # crear usuario auth
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, password=password)
            # crear adoptante vinculado
            adoptante = form.save(commit=False)
            adoptante.user = user
            adoptante.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('admin_panel:gestion_usuarios')
    else:
        form = CrearUsuarioForm()
    return render(request, 'admin_panel/crear_usuario.html', {'form': form})

@admin_required
# admin_panel/views.py

def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    adoptante = get_object_or_404(Adoptante, user=usuario)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=usuario)
        adoptante_form = AdoptanteForm(request.POST, request.FILES, instance=adoptante)
        if user_form.is_valid() and adoptante_form.is_valid():
            user_form.save()
            adoptante_form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('admin_panel:gestion_usuarios')
    else:
        user_form = UserForm(instance=usuario)
        adoptante_form = AdoptanteForm(instance=adoptante)

    return render(request, "admin_panel/editar_usuario.html", {
        "user_form": user_form,
        "adoptante_form": adoptante_form,
    })


@admin_required
def eliminar_usuario(request, user_id):
    if request.method != 'POST':
        messages.error(request, "Petición inválida para eliminar usuario.")
        return redirect('admin_panel:gestion_usuarios')
    
    usuario = get_object_or_404(User, id=user_id)  # buscá el usuario
    adoptante = get_object_or_404(Adoptante, user=usuario)  # su adoptante
    usuario.delete()  # esto también elimina adoptante si tenés cascada en modelo, sino borrás manualmente adoptante
    messages.success(request, "Usuario eliminado.")
    return redirect('admin_panel:gestion_usuarios')


# ---------- REFUGIOS ----------

@admin_required
def gestion_refugios(request):
    refugios = Refugio.objects.select_related('usuario').all() # Mejorado para select_related
    return render(request, 'admin_panel/refugios.html', {'refugios': refugios})

@admin_required
def crear_refugio(request):
    if request.method == 'POST':
        user_form = CrearRefugioUserForm(request.POST)
        refugio_form = RefugioForm(request.POST)
        
        if user_form.is_valid() and refugio_form.is_valid():
            # ✅ Crear el usuario del refugio
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            user.set_password(password)
            user.is_staff = True  # Para permitir acceso al panel
            user.save()

            # ✅ Crear el refugio vinculado al usuario
            refugio = refugio_form.save(commit=False)
            refugio.usuario = user
            refugio.save()

            messages.success(request, "Refugio y Usuario creados correctamente.")
            return redirect('admin_panel:gestion_refugios')
        else:
            print("===================================")
            print("ERRORES DEL USER_FORM:", user_form.errors)
            print("ERRORES DEL REFUGIO_FORM:", refugio_form.errors)
            print("===================================")
    else:
        user_form = CrearRefugioUserForm() 
        refugio_form = RefugioForm()
        
    return render(request, 'admin_panel/crear_refugio.html', {
        'user_form': user_form, 
        'refugio_form': refugio_form
    })



# admin_panel/views.py

@admin_required
def editar_refugio(request, refugio_id):
    refugio = get_object_or_404(Refugio, usuario_id=refugio_id)
    usuario = refugio.usuario 
    
    if request.method == 'POST':
        user_form = EditarUserForm(request.POST, instance=usuario)
        refugio_form = RefugioForm(request.POST, instance=refugio)
        
        if user_form.is_valid() and refugio_form.is_valid():
            user_form.save()
            refugio_form.save()
            messages.success(request, "Refugio actualizado.")
            return redirect('admin_panel:gestion_refugios')
        else:
            # 🔑 CÓDIGO DE DEPURACIÓN AÑADIDO (para ver en la consola del servidor)
            print("===================================")
            print("¡ERROR DE VALIDACIÓN AL ACTUALIZAR!")
            print("ERRORES DEL USER_FORM:", user_form.errors)
            print("ERRORES DEL REFUGIO_FORM:", refugio_form.errors)
            print("===================================")
            # 🔑 MENSAJE DE ERROR WEB
            messages.error(request, "Hubo un error en los datos. Revise los campos marcados.")
            
    else:
        user_form = EditarUserForm(instance=usuario)
        refugio_form = RefugioForm(instance=refugio)
        
    return render(request, 'admin_panel/editar_refugio.html', {
        'user_form': user_form,
        'refugio_form': refugio_form,
        'refugio': refugio
    })

@admin_required
def eliminar_refugio(request, refugio_id):
    if request.method != 'POST':
        messages.error(request, "Petición inválida para eliminar refugio.")
        return redirect('admin_panel:gestion_refugios')
    refugio = get_object_or_404(Refugio, usuario_id=refugio_id)
    # 🔑 CORRECCIÓN: Eliminamos el usuario, lo que por CASCADE debe eliminar el refugio.
    # Asume que Refugio tiene un CASCADE.
    refugio.usuario.delete() 
    messages.success(request, "Refugio eliminado.")
    return redirect('admin_panel:gestion_refugios')


# ---------- MASCOTAS ----------
@admin_required
def gestion_mascotas(request):
    mascotas = Mascota.objects.select_related('refugio').all()
    return render(request, 'admin_panel/mascotas.html', {'mascotas': mascotas})

@admin_required
def crear_mascota(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Mascota creada.")
            return redirect('admin_panel:gestion_mascotas')
    else:
        form = MascotaForm()
    # 1. Obtiene todos los refugios.
    refugios_disponibles = Refugio.objects.all() 
    
    # 2. Renderiza la plantilla, pasando tanto el formulario como los refugios.
    context = {
        'form': form,
        'refugios': refugios_disponibles, # <- ESTO ES CLAVE para el HTML
    }
    return render(request, 'admin_panel/crear_mascota.html', context)

@admin_required
def editar_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            messages.success(request, "Mascota actualizada.")
            return redirect('admin_panel:gestion_mascotas')
    else:
        form = MascotaForm(instance=mascota)
    return render(request, 'admin_panel/editar_mascota.html', {'form': form, 'mascota': mascota})

@admin_required
def eliminar_mascota(request, mascota_id):
    if request.method != 'POST':
        messages.error(request, "Petición inválida para eliminar mascota.")
        return redirect('admin_panel:gestion_mascotas')
    mascota = get_object_or_404(Mascota, id=mascota_id)
    mascota.delete()
    messages.success(request, "Mascota eliminada.")
    return redirect('admin_panel:gestion_mascotas')


# ---------- SOLICITUDES ----------
@admin_required
def gestion_solicitudes(request):
    solicitudes = SolicitudAdopcion.objects.select_related('mascota').all()
    return render(request, 'admin_panel/solicitudes.html', {'solicitudes': solicitudes})

@admin_required
def editar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAdopcion, id=solicitud_id)
    if request.method == 'POST':
        form = SolicitudForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            messages.success(request, "Solicitud actualizada.")
            return redirect('admin_panel:gestion_solicitudes')
    else:
        form = SolicitudForm(instance=solicitud)
    return render(request, 'admin_panel/editar_solicitud.html', {'form': form, 'solicitud': solicitud})

@admin_required
def eliminar_solicitud(request, solicitud_id):
    if request.method != 'POST':
        messages.error(request, "Petición inválida para eliminar solicitud.")
        return redirect('admin_panel:gestion_solicitudes')
    solicitud = get_object_or_404(SolicitudAdopcion, id=solicitud_id)
    solicitud.delete()
    messages.success(request, "Solicitud eliminada.")
    return redirect('admin_panel:gestion_solicitudes')

# admin_panel/views.py

@admin_required
def editar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAdopcion, id=solicitud_id)
    if request.method == 'POST':
        # CAMBIO CLAVE: Usar el formulario con menos campos
        form = SolicitudAdminForm(request.POST, instance=solicitud) 
        if form.is_valid():
            form.save()
            messages.success(request, "Solicitud actualizada.")
            return redirect('admin_panel:gestion_solicitudes')
    else:
        # CAMBIO CLAVE: Usar el formulario con menos campos
        form = SolicitudAdminForm(instance=solicitud) 

    return render(request, 'admin_panel/editar_solicitud.html', {'form': form, 'solicitud': solicitud})