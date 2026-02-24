from .models import Usuario

class UserInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        usuario_id = request.session.get('usuario_id')
        
        # Usamos el sistema de usuario anónimo de Django para consistencia
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        
        if usuario_id:
            try:
                # Adjuntamos el objeto de usuario para fácil acceso en las plantillas
                request.user = Usuario.objects.get(id=usuario_id)
            except Usuario.DoesNotExist:
                # Si el usuario_id en la sesión es inválido, lo limpiamos para evitar errores.
                request.session.flush()

        response = self.get_response(request)
        return response