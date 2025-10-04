import os
import django
import pydoc
import pkgutil

# Configuramos Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_adopcion.settings')
django.setup()

# Lista de apps que querés documentar
apps = ['usuarios']  # agregá más apps si tenés

for app in apps:
    try:
        # Importamos el módulo de la app
        module = __import__(app)
        # Recorremos todos los submódulos
        for loader, name, is_pkg in pkgutil.walk_packages(module.__path__, module.__name__ + '.'):
            print(f'Generando doc para: {name}')
            pydoc.writedoc(name)
    except Exception as e:
        print(f'Error generando doc para {app}: {e}')

