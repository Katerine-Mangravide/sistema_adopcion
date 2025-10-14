from django.contrib.auth.models import User
from usuarios.models import Refugio

# Lista con los datos de los refugios
refugios_data = [
    {
        "username": "refugio_sanfrancisco",
        "password": "12345",
        "nombre": "Refugio San Francisco",
        "direccion": "Av. Central 123, Asunción",
        "telefono": "0981-123456",
        "email": "sanfrancisco@refugios.com",
    },
    {
        "username": "huellitas_felices",
        "password": "12345",
        "nombre": "Huellitas Felices",
        "direccion": "Calle del Sol 456, Luque",
        "telefono": "0982-654321",
        "email": "huellitas@refugios.com",
    },
    {
        "username": "patitas_del_corazon",
        "password": "12345",
        "nombre": "Patitas del Corazón",
        "direccion": "Ruta 2 km 10, San Lorenzo",
        "telefono": "0971-888999",
        "email": "patitas@refugios.com",
    },
    {
        "username": "esperanza_animal",
        "password": "12345",
        "nombre": "Esperanza Animal",
        "direccion": "Calle Primavera 789, Capiatá",
        "telefono": "0961-456789",
        "email": "esperanza@refugios.com",
    },
    {
        "username": "amigos_peludos",
        "password": "12345",
        "nombre": "Amigos Peludos",
        "direccion": "Av. Libertad 222, Fernando de la Mora",
        "telefono": "0992-111222",
        "email": "peludos@refugios.com",
    },
]

# Crear los refugios y sus usuarios
for data in refugios_data:
    # Crear o recuperar el usuario
    user, created = User.objects.get_or_create(username=data["username"], defaults={"email": data["email"]})
    if created:
        user.set_password(data["password"])
        user.save()
        print(f"✅ Usuario creado: {user.username}")
    else:
        print(f"⚠️ Usuario existente: {user.username}")

    # Crear o recuperar el refugio
    refugio, created = Refugio.objects.get_or_create(
        usuario=user,
        defaults={
            "nombre": data["nombre"],
            "direccion": data["direccion"],
            "telefono": data["telefono"],
            "email": data["email"],
            "es_refugio": True,
        },
    )
    if created:
        print(f"🏠 Refugio creado: {refugio.nombre}")
    else:
        print(f"⚠️ Refugio existente: {refugio.nombre}")

print("✅ Carga de refugios completada correctamente.")
