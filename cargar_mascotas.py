# cargar_mascotas.py
from usuarios.models import Refugio
from mascotas.models import Mascota

# Obtenemos algunos refugios ya creados
refugios = list(Refugio.objects.all())

if len(refugios) < 1:
    print("❌ No hay refugios disponibles. Crea primero algunos refugios.")
else:
    mascotas_data = [
        # 🔑 CORRECCIÓN: 'descripcion' debe ser una lista: ["Texto..."]
        {"nombre": "Rocky", "especie": "Perro", "raza": "Labrador", "edad": 4, "sexo": "M", "descripcion": ["Perro jugueton y amigable."], "refugio": refugios[0]},
        {"nombre": "Mia", "especie": "Gato", "raza": "Siames", "edad": 2, "sexo": "H", "descripcion": ["Gatita muy cariñosa y tranquila."], "refugio": refugios[0]},
        {"nombre": "Max", "especie": "Perro", "raza": "Bulldog", "edad": 3, "sexo": "M", "descripcion": ["Perro fuerte y leal."], "refugio": refugios[1]},
        {"nombre": "Luna", "especie": "Gato", "raza": "Persa", "edad": 1, "sexo": "H", "descripcion": ["Gata suave y dormilona."], "refugio": refugios[1]},
        {"nombre": "Coco", "especie": "Perro", "raza": "Beagle", "edad": 5, "sexo": "M", "descripcion": ["Perro curioso y activo."], "refugio": refugios[0]},
        {"nombre": "Nala", "especie": "Gato", "raza": "Mestizo", "edad": 2, "sexo": "H", "descripcion": ["Gata juguetona y amigable."], "refugio": refugios[1]},
        {"nombre": "Toby", "especie": "Perro", "raza": "Pastor Aleman", "edad": 6, "sexo": "M", "descripcion": ["Perro protector y obediente."], "refugio": refugios[0]},
        {"nombre": "Simba", "especie": "Gato", "raza": "Maine Coon", "edad": 3, "sexo": "M", "descripcion": ["Gato grande y amigable."], "refugio": refugios[1]},
        {"nombre": "Loki", "especie": "Perro", "raza": "Husky", "edad": 4, "sexo": "M", "descripcion": ["Perro enérgico y jugueton."], "refugio": refugios[0]},
        {"nombre": "Bella", "especie": "Gato", "raza": "Bengala", "edad": 2, "sexo": "H", "descripcion": ["Gata activa y curiosa."], "refugio": refugios[1]},
    ]

    for m in mascotas_data:
        mascota = Mascota.objects.create(
            nombre=m["nombre"],
            especie=m["especie"],
            raza=m["raza"],
            edad=m["edad"],
            sexo=m["sexo"],
            descripcion=m["descripcion"], # Esto ahora es una lista
            refugio=m["refugio"],
            imagen="img/placeholder.png" 
        )
        print(f"✅ Mascota creada: {mascota.nombre} ({mascota.especie})")

    print("✅ Carga de mascotas completada correctamente.")