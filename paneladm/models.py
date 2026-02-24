from django.db import models
from django.utils import timezone

class Reunion(models.Model):
    detalle = models.CharField(max_length=200, verbose_name="Título o Detalle")
    descripcion = models.TextField(verbose_name="Descripción")
    fecha = models.DateTimeField(verbose_name="Fecha y Hora")
    ubicacion = models.CharField(max_length=255, verbose_name="Ubicación")
    imagen = models.ImageField(upload_to='reuniones/', null=True, blank=True, verbose_name="Imagen (Opcional)")
    asistentes = models.ManyToManyField('usuario.Usuario', related_name='reuniones_asistidas', blank=True)
    interesados = models.ManyToManyField('usuario.Usuario', related_name='reuniones_interesado', blank=True)
    imprimir_etiqueta_al_asistir = models.BooleanField(
        default=True,
        verbose_name="¿Imprimir etiqueta al escanear QR?",
        help_text="Si se marca, se abrirá la ventana para imprimir la etiqueta del asistente al escanear su QR."
    )

    def __str__(self):
        return self.detalle

    class Meta:
        verbose_name = "Reunión"
        verbose_name_plural = "Reuniones"

class Encuesta(models.Model):
    reunion = models.OneToOneField(Reunion, on_delete=models.CASCADE, related_name="encuesta")
    titulo = models.CharField(max_length=200, default="Encuesta de Satisfacción")
    activa = models.BooleanField(default=True, help_text="Los usuarios solo pueden ver y responder encuestas activas.")
    creada_en = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Encuesta para: {self.reunion.detalle}"

class RespuestaEncuesta(models.Model):
    PUNTUACION_CHOICES = [
        (1, '1 - Muy Malo'),
        (2, '2 - Malo'),
        (3, '3 - Regular'),
        (4, '4 - Bueno'),
        (5, '5 - Excelente'),
    ]
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name="respuestas")
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, related_name="respuestas_encuesta")
    puntuacion = models.IntegerField(choices=PUNTUACION_CHOICES)
    comentarios = models.TextField(blank=True, null=True)
    fecha_respuesta = models.DateTimeField(default=timezone.now)
    destacado = models.BooleanField(default=False, help_text="Marcar para mostrar como testimonio en la página de inicio.")

    class Meta:
        unique_together = ('encuesta', 'usuario') # Un usuario solo puede responder una vez por encuesta

class SoporteTicket(models.Model):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_progreso', 'En Progreso'),
        ('cerrado', 'Cerrado'),
    ]

    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, related_name='tickets_soporte')
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket de {self.usuario.nombre}: {self.asunto}"

class TicketRespuesta(models.Model):
    ticket = models.ForeignKey(SoporteTicket, on_delete=models.CASCADE, related_name='respuestas')
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE)
    mensaje = models.TextField()
    imagen = models.ImageField(upload_to='soporte_respuestas/', null=True, blank=True, verbose_name="Imagen Adjunta")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_creacion']

    def __str__(self):
        return f"Respuesta de {self.usuario.nombre} en ticket #{self.ticket.id}"