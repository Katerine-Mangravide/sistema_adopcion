# mascotas/migrations/0008_...py

from django.db import migrations
from django.db.models import F, ForeignKey, CASCADE

def set_default_refugios(apps, schema_editor):
    """
    Establece el campo refugio de todas las mascotas existentes a NULL o default=1.
    """
    Mascota = apps.get_model('mascotas', 'Mascota')
    # 1. Limpia los datos rotos (los que no existen en la nueva tabla)
    # Ya que el campo es ahora null=True (por la migración 0007)
    Mascota.objects.filter(refugio_id__isnull=False).exclude(refugio_id__in=[1]).update(refugio_id=None)

    # 2. Asigna el valor por defecto (1) a los registros que quedaron sin Refugio ID válido
    Mascota.objects.filter(refugio_id__isnull=True).update(refugio_id=1)


class Migration(migrations.Migration):

    dependencies = [
        ('mascotas', '0007_auto_20251012_1503'), # Dependemos de la migración 0007
    ]

    operations = [
        # 1. Ejecutar la función de limpieza y asignación de default=1
        migrations.RunPython(set_default_refugios, reverse_code=migrations.RunPython.noop),

        # 2. Volver a hacer que el campo NO sea anulable
        migrations.AlterField(
            model_name='mascota',
            name='refugio',
            field=ForeignKey(on_delete=CASCADE, default=1, to='usuarios.refugio'),
        ),
    ]