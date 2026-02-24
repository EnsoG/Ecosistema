from django.contrib import admin
from django.urls import path, include
from usuario import views as usuario_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Rutas de Administración de Django
    path('admin/', admin.site.urls),

    # 2. Rutas principales de la aplicación (inicio, autenticación)
    path('', usuario_views.inicio, name='inicio'),
    path('registro/', usuario_views.registro, name='registro'),
    path('login/', usuario_views.login, name='login'),
    path('logout/', usuario_views.logout, name='logout'),

    # 3. Inclusión de las URLs de las otras aplicaciones
    # Las URLs de la app 'usuario' (perfil, config, etc.) se manejan aquí.
    path('', include('usuario.urls')), 
    # Las URLs del panel de administración personalizado.
    path('panel-admin/', include('paneladm.urls', namespace='panel-admin')),
]

# Configuración para servir archivos de medios (fotos de perfil, etc.) en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
