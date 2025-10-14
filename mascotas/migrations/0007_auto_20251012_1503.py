# mascotas/migrations/0007_auto_20251012_1503.py (Versión MODIFICADA)

from django.db import migrations
from django.db.models import F, ForeignKey, CASCADE

def set_null_refugios(apps, schema_editor):
    # ¡DEJA ESTA FUNCIÓN, PERO NO SE USARÁ EN ESTE ARCHIVO!
    Mascota = apps.get_model('mascotas', 'Mascota')
    Mascota.objects.update(refugio_id=None)

class Migration(migrations.Migration):

    dependencies = [
        # La migración que causó el conflicto, ahora falsificada
        ('mascotas', '0006_alter_mascota_refugio_mascota_descripcion_and_more'), 
    ]

    operations = [
        # SOLO DEJAMOS ESTA OPERACIÓN (hacer el campo temporalmente anulable)
        migrations.AlterField(
            model_name='mascota',
            name='refugio',
            # Es crucial que sea null=True aquí
            field=ForeignKey(null=True, on_delete=CASCADE, to='usuarios.refugio'), 
        ),
    ]