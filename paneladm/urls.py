from django.urls import path
from . import views
from usuario import views as usuario_views

app_name = 'panel-admin'

urlpatterns = [
    path('', usuario_views.panel_admin, name='panel_admin'), # The root of the admin panel
    path('usuarios/buscar/', views.buscar_usuarios_ajax, name='buscar_usuarios_ajax'),
    path('usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/crear/', views.crear_usuario_admin, name='crear_usuario_admin'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario_admin, name='editar_usuario_admin'),
    path('usuarios/exportar-excel/', views.exportar_usuarios_excel, name='exportar_usuarios_excel'),
    path('usuarios/toggle-destacado/<int:usuario_id>/', views.toggle_destacado_usuario, name='toggle_destacado_usuario'),
    path('usuarios/toggle-visibilidad/<int:usuario_id>/', views.toggle_visibilidad_usuario, name='toggle_visibilidad_usuario'),
    path('usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('reuniones/', views.gestion_reuniones, name='gestion_reuniones'),
    path('reuniones/editar/<int:reunion_id>/', views.editar_reunion, name='editar_reunion'),
    path('reuniones/eliminar/<int:reunion_id>/', views.eliminar_reunion, name='eliminar_reunion'),
    path('asistencia/', views.control_asistencia, name='control_asistencia'),
    path('reuniones/<int:reunion_id>/asistencia/', views.registrar_asistencia, name='registrar_asistencia'),
    path('asistentes/', views.gestion_asistentes, name='gestion_asistentes'),
    path('asistentes/<int:reunion_id>/', views.ver_asistentes_reunion, name='ver_asistentes_reunion'),
    path('asistentes/<int:reunion_id>/exportar-excel/', views.exportar_asistentes_reunion_excel, name='exportar_asistentes_reunion_excel'),
    path('reuniones/<int:reunion_id>/quitar-asistencia/<int:usuario_id>/', views.quitar_asistencia, name='quitar_asistencia'),
    path('reuniones/<int:reunion_id>/marcar-asistencia/<int:usuario_id>/', views.marcar_asistencia_qr, name='marcar_asistencia_qr'),
    path('interesados/', views.gestion_interesados, name='gestion_interesados'),
    path('encuestas/', views.gestion_encuestas, name='gestion_encuestas'),
    path('encuestas/<int:encuesta_id>/respuestas/', views.ver_respuestas_encuesta, name='ver_respuestas_encuesta'),
    path('encuestas/eliminar/<int:encuesta_id>/', views.eliminar_encuesta, name='eliminar_encuesta'),
    path('respuestas/toggle-destacado/<int:respuesta_id>/', views.toggle_destacado_respuesta, name='toggle_destacado_respuesta'),
    path('soporte/', views.gestion_soporte, name='gestion_soporte'),
    path('soporte/<int:ticket_id>/', views.ver_ticket_soporte, name='ver_ticket_soporte'),
    path('estadisticas/', views.estadisticas_admin, name='estadisticas_admin'),
    path('estadisticas/exportar-excel/', views.exportar_estadisticas_excel, name='exportar_estadisticas_excel'),
    # --- URLs para el Modo Tótem ---
    path('totem/seleccionar-reunion/', views.totem_seleccionar_reunion, name='totem_seleccionar_reunion'),
    path('totem/escaner/<int:reunion_id>/', views.totem_escaner, name='totem_escaner'),
    path('totem/verify-exit/', views.totem_verify_exit, name='totem_verify_exit'),
    # --- URL para la Ruleta de Sorteos ---
    path('ruleta/', views.ruleta_sorteo, name='ruleta_sorteo'),
    path('ruleta/obtener-participantes/', views.obtener_participantes_ruleta, name='obtener_participantes_ruleta'),
    # --- URLs Públicas de Reuniones ---
    path('reunion/<int:reunion_id>/publica/', views.reunion_publica, name='reunion_publica'),
    path('reunion/<int:reunion_id>/inscribirse/', views.inscribirse_reunion, name='inscribirse_reunion'),
]