from django.shortcuts import render, redirect
from .forms import LoginForm
from usuario.models import Usuario
from django.contrib.auth.hashers import check_password
from django.contrib import messages

def login_usuario(request):
    mensaje = ""
    if request.method == "POST":
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
                        return redirect('panel-admin:totem_seleccionar_reunion')
                    
                    return redirect('inicio') # Redirección por defecto
                else:
                    mensaje = "Email o contraseña incorrectos."
            except Usuario.DoesNotExist: 
                mensaje = "Email o contraseña incorrectos."
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'mensaje': mensaje})

def logout_usuario(request):
    request.session.flush()
    return redirect('inicio')
