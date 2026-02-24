from django.contrib import admin
from .models import Usuario

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'es_admin', 'es_ayudante', 'es_totem')
    list_filter = ('es_admin', 'es_ayudante', 'es_totem')
    search_fields = ('nombre', 'apellido', 'email', 'rut')
    ordering = ('apellido', 'nombre')
    exclude = ('password',)

admin.site.register(Usuario, UsuarioAdmin)
