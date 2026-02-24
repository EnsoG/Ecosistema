from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password, check_password
import qrcode
from io import BytesIO
from django.core.files import File
from django.urls import reverse
from django.conf import settings

RUBRO_CHOICES = [
    ('Tecnología y Desarrollo', (
        ('desarrollo_software', 'Desarrollo de Software'),
        ('desarrollo_web', 'Desarrollo Web'),
        ('desarrollo_movil', 'Desarrollo Móvil'),
        ('ia_machine_learning', 'Inteligencia Artificial / Machine Learning'),
        ('ciberseguridad', 'Ciberseguridad'),
        ('analisis_datos', 'Análisis de Datos / Big Data'),
        ('devops', 'DevOps'),
        ('infraestructura_cloud', 'Infraestructura y Cloud'),
        ('ecommerce', 'E-commerce'),
    )),
    ('Diseño y Creatividad', (
        ('diseno_grafico', 'Diseño Gráfico'),
        ('diseno_ux_ui', 'Diseño UX/UI'),
        ('produccion_audiovisual', 'Producción Audiovisual'),
        ('fotografia', 'Fotografía'),
        ('marketing_digital', 'Marketing Digital'),
        ('redes_sociales', 'Gestión de Redes Sociales'),
        ('publicidad', 'Publicidad'),
    )),
    ('Negocios y Consultoría', (
        ('consultoria_negocios', 'Consultoría de Negocios'),
        ('finanzas_contabilidad', 'Finanzas y Contabilidad'),
        ('recursos_humanos', 'Recursos Humanos'),
        ('ventas_desarrollo_negocios', 'Ventas y Desarrollo de Negocios'),
        ('legal_asesoria', 'Legal y Asesoría'),
        ('gestion_proyectos', 'Gestión de Proyectos'),
    )),
    ('Salud y Bienestar', (
        ('salud_medicina', 'Salud y Medicina'),
        ('psicologia_coaching', 'Psicología y Coaching'),
        ('nutricion', 'Nutrición'),
        ('deporte_fitness', 'Deporte y Fitness'),
    )),
    ('Otros Sectores', (
        ('educacion', 'Educación y Formación'),
        ('inmobiliario', 'Sector Inmobiliario'),
        ('turismo_hoteleria', 'Turismo y Hotelería'),
        ('gastronomia', 'Gastronomía'),
        ('construccion_arquitectura', 'Construcción y Arquitectura'),
        ('agroindustria', 'Agroindustria'),
        ('otro', 'Otro'),
    )),
]

class Usuario(models.Model):
    # Campos de Usuario
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    rubro = models.CharField(max_length=100, choices=RUBRO_CHOICES, blank=True, null=True, help_text="Tu profesión o área de expertise.", verbose_name="Rubro")
    rubro_otro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Especificar otro rubro")
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    etiqueta_emojis = models.CharField(max_length=10, blank=True)
    # Campos de Empresa
    nombre_empresa = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre de la Empresa/Pyme")
    rubro_empresa = models.CharField(max_length=100, blank=True, null=True, verbose_name="Rubro de la Empresa")
    descripcion_empresa = models.TextField(blank=True, null=True, verbose_name="Descripción de la Empresa")
    web_empresa = models.URLField(blank=True, null=True, verbose_name="Sitio Web de la Empresa")
    buscando = models.CharField(max_length=255, blank=True, null=True, verbose_name="¿Qué buscas en la comunidad?", help_text="Ej: Inversionistas, socios, clientes, etc.")
    # Campos de Sistema
    es_admin = models.BooleanField(default=False)
    es_ayudante = models.BooleanField(default=False)
    es_totem = models.BooleanField(default=False, help_text="Designa a este usuario como una cuenta para un quiosco/tótem de check-in.")
    cantidad_asistencias = models.IntegerField(default=0, verbose_name="Cantidad de Asistencias")
    perfil_publico = models.BooleanField(default=True, help_text="Permite que otros miembros vean tu perfil en el directorio.")
    destacado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Comprueba si la contraseña ha sido cambiada o si es un usuario nuevo.
        # Una contraseña hasheada siempre empieza con un algoritmo como 'pbkdf2_sha256$'.
        # Si no empieza así, significa que es una contraseña nueva en texto plano.
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            self.password = make_password(self.password)
        
        # Si se está editando un usuario existente y el campo de contraseña se dejó en blanco,
        # no queremos sobreescribir la contraseña existente.
        elif not self.password and self.pk:
            original_user = Usuario.objects.get(pk=self.pk)
            self.password = original_user.password

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    @property
    def get_rubro_real_display(self):
        if self.rubro == 'otro':
            return self.rubro_otro or 'Otro'
        return self.get_rubro_display()

@receiver(post_save, sender=Usuario)
def extras_post_creacion(sender, instance, created, **kwargs):
    import random
    if created:
        update_fields = []
        if not instance.etiqueta_emojis:
            emojis_disponibles = ['💡', '🚀', '📈', '💼', '🤝', '🌐', '💻', '📱', '🎯', '🌟', '🌱', '🔗', '🛠️', '📊', '🧠', '⚡️', '🏆', '🔑']
            instance.etiqueta_emojis = "".join(random.sample(emojis_disponibles, 3))
            update_fields.append('etiqueta_emojis')
        if not instance.qr_code:
            base_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')
            qr_url = base_url + reverse('perfil_publico', args=[instance.id])
            buffer = BytesIO()
            qrcode.make(qr_url).save(buffer, format='PNG')
            instance.qr_code.save(f'qr_usuario_{instance.id}.png', File(buffer), save=False)
            update_fields.append('qr_code')

        if update_fields:
            instance.save(update_fields=update_fields)
