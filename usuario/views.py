from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import UsuarioForm, EditarUsuarioForm, RespuestaEncuestaForm, CambiarPasswordForm, LoginForm
from .models import Usuario, RUBRO_CHOICES
from paneladm.models import Reunion, Encuesta, RespuestaEncuesta, SoporteTicket, TicketRespuesta
from paneladm.forms import SoporteTicketForm, TicketRespuestaForm, ReunionForm
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.db.models import Q
import random

def login_required(view_func):
    """
    Decorador personalizado para verificar que el usuario ha iniciado sesión.
    """
    def wrapper(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def login(request):
    if 'usuario_id' in request.session:
        return redirect('inicio')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                usuario = Usuario.objects.get(email=email)
                if check_password(password, usuario.password):
                    request.session['usuario_id'] = usuario.id
                    messages.success(request, f'¡Bienvenido de vuelta, {usuario.nombre}!')
                    
                    # --- LÓGICA DE REDIRECCIÓN POR ROL ---
                    if usuario.es_totem:
                        return redirect('totem_seleccionar_reunion')
                    return redirect('inicio')
                else:
                    messages.error(request, 'La contraseña es incorrecta.')
            except Usuario.DoesNotExist:
                messages.error(request, 'No existe un usuario con ese correo electrónico.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout(request):
    """Cierra la sesión del usuario."""
    if 'usuario_id' in request.session:
        del request.session['usuario_id']
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('inicio')

def registro(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            request.session['usuario_id'] = usuario.id
            
            # Mensaje de bienvenida simple
            messages.success(request, f'¡Bienvenido, {usuario.nombre}! Tu registro fue exitoso.')

            return redirect('inicio')
        # Si el formulario NO es válido, se renderiza la misma página con los errores
        # pero el 'form' ahora contiene los errores y los datos anteriores.
    else:
        form = UsuarioForm()
    return render(request, 'registro.html', {'form': form})


def perfil(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST' and 'responder_encuesta' in request.POST:
        form_respuesta = RespuestaEncuestaForm(request.POST)
        if form_respuesta.is_valid():
            encuesta_id = request.POST.get('encuesta_id')
            encuesta = get_object_or_404(Encuesta, id=encuesta_id)
            respuesta = form_respuesta.save(commit=False)
            respuesta.encuesta = encuesta
            respuesta.usuario = usuario
            respuesta.save()
            
            messages.success(request, '¡Gracias por tu respuesta!')
            return redirect('perfil')
    
    elif request.method == 'POST' and 'toggle_privacy' in request.POST:
        # Lógica para cambiar la privacidad del perfil
        es_publico = 'perfil_publico' in request.POST
        usuario.perfil_publico = es_publico
        usuario.save(update_fields=['perfil_publico']) 
        messages.success(request, 'Tu configuración de privacidad ha sido actualizada.')
        return redirect('perfil')

    reuniones_asistidas = usuario.reuniones_asistidas.all()
    encuestas_pendientes = []
    for reunion in reuniones_asistidas:
        if hasattr(reunion, 'encuesta') and reunion.encuesta.activa and not reunion.encuesta.respuestas.filter(usuario=usuario).exists():
            encuestas_pendientes.append(reunion.encuesta)

    form_respuesta = RespuestaEncuestaForm()
    return render(request, 'perfil.html', {
        'usuario': usuario, 'encuestas_pendientes': encuestas_pendientes, 'form_resp_encuesta': form_respuesta
    })

def editar_perfil(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Perfil actualizado con éxito!')
            return redirect('perfil')
    else:
        form = EditarUsuarioForm(instance=usuario)
    return render(request, 'editar_perfil.html', {'form': form, 'usuario': usuario})

def perfil_publico(request, usuario_id):
    # MODO MANTENIMIENTO
    # return render(request, 'mantenimiento.html')
    usuario_logueado = None
    if 'usuario_id' in request.session:
        usuario_logueado = get_object_or_404(Usuario, id=request.session.get('usuario_id'))

    perfil_visitado = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'perfil_publico.html', {'perfil_visitado': perfil_visitado, 'usuario': usuario_logueado})

def imprimir_etiqueta(request, usuario_id):
    """
    Vista que muestra solo la etiqueta de un usuario para impresión directa.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'etiqueta_imprimir.html', {'usuario': usuario})

def inicio(request):
    usuario_id = request.session.get('usuario_id')
    usuario = None
    if usuario_id:
        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            pass

    reuniones_proximas = Reunion.objects.filter(fecha__gte=timezone.now()).order_by('fecha')
    now = timezone.now()
    for reunion in reuniones_proximas:
        delta = reunion.fecha.date() - now.date()
        reunion.dias_restantes = delta.days

    testimonios = RespuestaEncuesta.objects.filter(destacado=True).exclude(comentarios__exact='').order_by('-fecha_respuesta')
    total_usuarios = Usuario.objects.count()
    total_reuniones = Reunion.objects.count()
    contexto = {
        'usuario': usuario,
        'reuniones': reuniones_proximas,
        'testimonios': testimonios,
        'total_usuarios': total_usuarios,
        'total_reuniones': total_reuniones,
    }
    return render(request, 'inicio.html', contexto)

def landing_reuniones(request):
    now = timezone.now()
    reuniones_proximas = Reunion.objects.filter(fecha__gte=now).order_by('fecha')
    reuniones_pasadas = Reunion.objects.filter(fecha__lt=now).order_by('-fecha')
    contexto = {
        'reuniones_proximas': reuniones_proximas,
        'reuniones_pasadas': reuniones_pasadas,
    }
    return render(request, 'landing_reuniones.html', contexto)

def registrar_interes(request, reunion_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, 'Debes iniciar sesión para mostrar interés en una reunión.')
        return redirect('login')
    if request.method == 'POST':
        reunion = get_object_or_404(Reunion, id=reunion_id)
        usuario = get_object_or_404(Usuario, id=usuario_id)
        reunion.interesados.add(usuario)
        messages.success(request, f'¡Genial! Has mostrado interés en "{reunion.detalle}".')
    return redirect('inicio')


@login_required
def toggle_interes(request, reunion_id):
    """
    Registra o quita el interés de un usuario en una reunión (AJAX).
    """
    from django.http import JsonResponse
    if request.method == 'POST':
        reunion = get_object_or_404(Reunion, id=reunion_id)
        usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))

        if usuario in reunion.asistentes.all():
            return JsonResponse({'status': 'error', 'message': 'Tu asistencia ya está confirmada.'}, status=400)

        if usuario in reunion.interesados.all():
            reunion.interesados.remove(usuario)
            return JsonResponse({'status': 'removed', 'message': 'Interés quitado.'})
        else:
            reunion.interesados.add(usuario)
            return JsonResponse({'status': 'added', 'message': 'Interés registrado.'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

def panel_admin(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    try:
        usuario_actual = Usuario.objects.get(id=usuario_id)
        if not usuario_actual.es_admin and not usuario_actual.es_ayudante:
            return redirect('inicio')
    except Usuario.DoesNotExist:
        return redirect('login')

    # Datos para el dashboard
    total_usuarios = Usuario.objects.filter(es_admin=False, es_ayudante=False, es_totem=False).count()
    reuniones_programadas = Reunion.objects.filter(fecha__gte=timezone.now()).count()
    tickets_abiertos = SoporteTicket.objects.filter(estado='abierto').count()

    contexto = {'usuario': usuario_actual, 'total_usuarios': total_usuarios,
                'reuniones_programadas': reuniones_programadas, 'tickets_abiertos': tickets_abiertos}

    return render(request, 'panel_admin.html', contexto)

@login_required
def configuracion(request):
    """
    Muestra la página de configuración del usuario.
    """
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        usuario.perfil_publico = request.POST.get('perfil_publico') == 'true'
        usuario.save(update_fields=['perfil_publico'])
        messages.success(request, 'Tu configuración de privacidad ha sido actualizada.')
        return redirect('configuracion')

    contexto = {
        'usuario': usuario
    }
    return render(request, 'configuracion.html', contexto)

@login_required
def cambiar_password(request):
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            password_actual = form.cleaned_data['password_actual']
            nueva_password = form.cleaned_data['nueva_password']

            if not check_password(password_actual, usuario.password):
                messages.error(request, 'La contraseña actual es incorrecta.')
            else:
                from django.contrib.auth.hashers import make_password
                usuario.password = nueva_password
                usuario.save()
                messages.success(request, '¡Contraseña actualizada con éxito!')
                return redirect('configuracion')
    else:
        form = CambiarPasswordForm()
    
    contexto = {
        'form': form,
        'usuario': usuario
    }
    return render(request, 'cambiar_password.html', contexto)

@login_required
def eliminar_cuenta(request):
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        usuario = get_object_or_404(Usuario, id=usuario_id)
        usuario.delete()
        request.session.flush()
        messages.success(request, 'Tu cuenta ha sido eliminada permanentemente.')
        return redirect('inicio')
    return redirect('configuracion')

@login_required
def crear_ticket_soporte(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    if request.method == 'POST':
        form = SoporteTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.usuario = usuario
            ticket.save()
            messages.success(request, 'Tu ticket de soporte ha sido enviado. Te responderemos pronto.')
            return redirect('ver_ticket_usuario', ticket_id=ticket.id)
    else:
        form = SoporteTicketForm()
    
    contexto = {
        'form': form,
        'usuario': usuario
    }
    return render(request, 'crear_ticket.html', contexto)

@login_required
def mis_tickets(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    tickets = SoporteTicket.objects.filter(usuario=usuario).order_by('-fecha_creacion')
    return render(request, 'mis_tickets.html', {'usuario': usuario, 'tickets': tickets})

@login_required
def ver_ticket_usuario(request, ticket_id):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    ticket = get_object_or_404(SoporteTicket, id=ticket_id, usuario=usuario) # Seguridad: solo el dueño puede ver

    if request.method == 'POST':
        respuesta_form = TicketRespuestaForm(request.POST, request.FILES)
        if respuesta_form.is_valid():
            respuesta = respuesta_form.save(commit=False)
            respuesta.ticket = ticket
            respuesta.usuario = usuario
            respuesta.save()
            messages.success(request, 'Tu respuesta ha sido enviada.')
            return redirect('ver_ticket_usuario', ticket_id=ticket.id)

    respuesta_form = TicketRespuestaForm()
    contexto = {
        'ticket': ticket,
        'respuesta_form': respuesta_form,
        'usuario': usuario,
    }
    return render(request, 'ver_ticket_usuario.html', contexto)

@login_required
def directorio_miembros(request):
    # --- CÓDIGO CORREGIDO Y MEJORADO ---
    usuario_id = request.session.get('usuario_id')
    usuario_actual = get_object_or_404(Usuario, id=usuario_id) # El que está viendo la página

    query = request.GET.get('q', '')
    rubro_filter = request.GET.get('rubro', '')

    # Base de miembros: excluimos roles especiales que no deben aparecer en el directorio.
    base_miembros = Usuario.objects.filter(es_admin=False, es_ayudante=False, es_totem=False)

    # Los usuarios normales solo ven perfiles públicos. El admin ve todos los perfiles (públicos y privados).
    if usuario_actual.es_admin:
        # El admin ve a todos los usuarios, ordenando por destacado, luego por visibilidad y finalmente por nombre.
        miembros = base_miembros.order_by('-destacado', '-perfil_publico', 'nombre')
    else:
        miembros = base_miembros.filter(perfil_publico=True).order_by('-destacado', 'nombre')

    if query:
        miembros = miembros.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(nombre_empresa__icontains=query) |
            Q(rubro__icontains=query)  # Corregido: buscar en el rubro del usuario
        )

    if rubro_filter:
        miembros = miembros.filter(rubro__iexact=rubro_filter)

    # Obtenemos todos los rubros posibles desde el modelo para el filtro del directorio.
    todos_los_rubros = [choice[0] for group in RUBRO_CHOICES for choice in group[1]]

    contexto = {
        'usuario': usuario_actual,
        'miembros': miembros,
        'rubros': todos_los_rubros,
    }
    return render(request, 'directorio.html', contexto)

@login_required
def mis_reuniones(request):
    """
    Muestra al usuario un resumen de su actividad en las reuniones.
    """
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))

    # Reuniones futuras en las que el usuario ha mostrado interés O ya es asistente.
    # Usamos Q para combinar ambas consultas y .distinct() para evitar duplicados.
    reuniones_futuras_actividad = Reunion.objects.filter(
        Q(interesados=usuario) | Q(asistentes=usuario),
        fecha__gte=timezone.now()
    ).distinct().order_by('fecha')

    # Historial de reuniones a las que el usuario ha asistido
    # Usamos select_related para optimizar y evitar consultas extra en el bucle de la plantilla
    reuniones_asistidas = usuario.reuniones_asistidas.filter(fecha__lt=timezone.now()).order_by('-fecha').select_related('encuesta')

    # Obtenemos los IDs de las encuestas que el usuario ya ha respondido
    encuestas_respondidas_ids = set(RespuestaEncuesta.objects.filter(usuario=usuario).values_list('encuesta_id', flat=True))

    contexto = {
        'usuario': usuario,
        'reuniones_interesado': reuniones_futuras_actividad,
        'reuniones_asistidas': reuniones_asistidas,
        'encuestas_respondidas_ids': encuestas_respondidas_ids,
    }
    return render(request, 'mis_reuniones.html', contexto)