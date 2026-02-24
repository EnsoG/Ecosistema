from paneladm.models import SoporteTicket

def notificaciones_admin(request):
    """
    Añade el número de tickets de soporte abiertos al contexto
    si el usuario es un administrador.
    """
    if hasattr(request, 'user_is_admin') and request.user_is_admin:
        tickets_abiertos = SoporteTicket.objects.filter(estado='abierto').count()
        return {'tickets_abiertos_count': tickets_abiertos}
    return {}