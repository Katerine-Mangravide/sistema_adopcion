# mascotas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Mascota, SolicitudAdopcion
from .forms import SolicitudAdopcionForm
from usuarios.models import Adoptante

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
            return redirect('uusuarios:solicitud_enviada')
    else:
        form = SolicitudAdopcionForm(initial={'telefono': adoptante.telefono, 'direccion': adoptante.direccion})
        

    return render(request, 'mascotas/solicitar_adopcion.html', {'form': form, 'mascota': mascota, 'adoptante': adoptante})
