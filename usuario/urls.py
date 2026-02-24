from django.urls import path
from . import views

urlpatterns = [
    path('reuniones/', views.landing_reuniones, name='landing_reuniones'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/<int:usuario_id>/', views.editar_perfil, name='editar_perfil'),
    path('perfil-publico/<int:usuario_id>/', views.perfil_publico, name='perfil_publico'),
    path('imprimir-etiqueta/<int:usuario_id>/', views.imprimir_etiqueta, name='imprimir_etiqueta'),
    path('reunion/<int:reunion_id>/toggle-interes/', views.toggle_interes, name='toggle_interes'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('configuracion/cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('configuracion/eliminar-cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path('soporte/crear/', views.crear_ticket_soporte, name='crear_ticket_soporte'),
    path('soporte/mis-tickets/', views.mis_tickets, name='mis_tickets'),
    path('soporte/ticket/<int:ticket_id>/', views.ver_ticket_usuario, name='ver_ticket_usuario'),
    path('directorio/', views.directorio_miembros, name='directorio_miembros'),
    path('mis-reuniones/', views.mis_reuniones, name='mis_reuniones'),
]
