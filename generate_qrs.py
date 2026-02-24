import os
import django

# Configura el entorno de Django para poder usar los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ecosistema.settings')
django.setup()

from usuario.models import Usuario
import random

def generate_qr_for_all_users():
    """
    Recorre todos los usuarios y vuelve a guardar cada uno para
    disparar la lógica de generación de QR en el método save().
    """
    usuarios = Usuario.objects.all()
    total = usuarios.count()
    
    if total == 0:
        print("No hay usuarios en la base de datos.")
        return

    print(f"Se encontraron {total} usuarios. Generando códigos QR...")

    for i, usuario in enumerate(usuarios):
        print(f"[{i+1}/{total}] Procesando a: {usuario.email}")
        try:
            # Asigna emojis si el campo está vacío
            if not usuario.etiqueta_emojis:
                emojis_disponibles = ['💡', '🚀', '📈', '💼', '🤝', '🌐', '💻', '📱', '🎯', '🌟', '🌱', '🔗', '🛠️', '📊', '🧠', '⚡️', '🏆', '🔑']
                usuario.etiqueta_emojis = "".join(random.sample(emojis_disponibles, 3))
                print(f"  -> Emojis asignados: {usuario.etiqueta_emojis}")

            # Al guardar el objeto, se activa la lógica del método save() en el modelo.
            usuario.save()
            print("  -> QR y datos guardados.")

        except Exception as e:
            print(f"  ERROR al generar QR para {usuario.email}: {e}")

    print("\n¡Proceso completado!")

if __name__ == '__main__':
    generate_qr_for_all_users()