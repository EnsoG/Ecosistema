# En c:\Users\joaqu\Desktop\Ecosistema\Ecosistema\Ecosistema\usuario\forms.py

from django import forms
from .models import Usuario
from paneladm.models import RespuestaEncuesta
import re

def validate_rut(rut):
    """
    Valida un RUT chileno.
    Retorna (True, "RUT limpio") si es válido, o (False, "Mensaje de error") si no lo es.
    """
    rut_limpio = str(rut).upper().replace(".", "").replace("-", "")
    
    if not rut_limpio[:-1].isdigit() or not (rut_limpio[-1].isdigit() or rut_limpio[-1] == 'K'):
        return False, "El RUT debe contener solo números y, si corresponde, una 'K' al final."

    # Si el RUT viene formateado (ej: 12.345.678-9), el último caracter es el DV.
    # Si viene limpio (ej: 123456789), también.
    body = rut_limpio[:-1]
    dv = rut_limpio[-1]

    try:
        reversed_body = map(int, reversed(body))
        factors = [2, 3, 4, 5, 6, 7] * (len(body) // 6 + 1)
        s = sum(digit * factor for digit, factor in zip(reversed_body, factors))
        res = 11 - (s % 11)
        
        calculated_dv = str(res) if res < 10 else ('0' if res == 11 else 'K')

        if dv == calculated_dv:
            return True, rut_limpio
        else:
            return False, "El RUT ingresado no es válido (dígito verificador incorrecto)."
    except ValueError:
        return False, "Formato de RUT incorrecto."

class LoginForm(forms.Form):
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'}))


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'nombre', 'apellido', 'rubro', 'rubro_otro', 'rut', 'email', 'telefono', 'foto',
            'nombre_empresa', 'descripcion_empresa', 'web_empresa', 'buscando'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'rubro': forms.Select(attrs={'class': 'form-select'}),
            'rubro_otro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escribe tu rubro aquí'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            # Widgets para los nuevos campos de empresa
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_empresa': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'web_empresa': forms.URLInput(attrs={'class': 'form-control'}),
            'buscando': forms.TextInput(attrs={'class': 'form-control'}),
        }
        # El widget de 'foto' se maneja mejor en el __init__ para que no aparezca en el HTML por defecto.

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        is_valid, message_or_rut = validate_rut(rut)
        if not is_valid:
            raise forms.ValidationError(message_or_rut)

        # Verificar si el RUT ya existe en la base de datos
        if Usuario.objects.filter(rut=message_or_rut).exists():
            raise forms.ValidationError("Ya existe un usuario con este RUT.")

        return message_or_rut

    def clean_email(self):
        # Usamos .lower() para una comparación insensible a mayúsculas/minúsculas
        email = self.cleaned_data.get('email').lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo electrónico.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        rubro = cleaned_data.get("rubro")
        rubro_otro = cleaned_data.get("rubro_otro")

        if rubro == 'otro' and not rubro_otro:
            self.add_error('rubro_otro', 'Debes especificar tu rubro si seleccionas "Otro".')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ocultamos el input de archivo por defecto para estilizarlo con un botón.
        self.fields['foto'].widget = forms.FileInput(attrs={'class': 'd-none'})

    def save(self, commit=True):
        usuario = super().save(commit=False)
        rut_limpio = self.cleaned_data.get('rut')
        # La contraseña será el RUT sin el dígito verificador.
        password = rut_limpio[:-1]
        usuario.set_password(password)
        if commit:
            usuario.save()
        return usuario


class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'nombre', 'apellido', 'rubro', 'rubro_otro', 'rut', 'email', 'telefono', 'foto',
            'nombre_empresa', 'descripcion_empresa', 'web_empresa', 'buscando'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'rubro': forms.Select(attrs={'class': 'form-select'}),
            'rubro_otro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escribe tu rubro aquí'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control d-none'}),
            # Widgets para los nuevos campos de empresa
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_empresa': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'web_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: miempresa.com'}),
            'buscando': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        is_valid, message_or_rut = validate_rut(rut)
        if not is_valid:
            raise forms.ValidationError(message_or_rut)
        
        # Al editar, debemos excluir al propio usuario de la verificación de duplicados.
        # 'self.instance' es el objeto de usuario que se está editando.
        if self.instance:
            if Usuario.objects.filter(rut=message_or_rut).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ya existe otro usuario con este RUT.")
        elif Usuario.objects.filter(rut=message_or_rut).exists():
             raise forms.ValidationError("Ya existe un usuario con este RUT.")

        return message_or_rut

class AyudanteUsuarioForm(EditarUsuarioForm):
    """Formulario para que los ayudantes editen usuarios, sin campos sensibles."""
    class Meta(EditarUsuarioForm.Meta):
        # Hereda los campos de EditarUsuarioForm y añade 'cantidad_asistencias'
        fields = EditarUsuarioForm.Meta.fields + ['cantidad_asistencias']


class AdminUsuarioForm(forms.ModelForm):
    # Hacemos el campo de contraseña no requerido y añadimos un placeholder
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dejar en blanco para no cambiar'}), required=False)

    class Meta:
        model = Usuario
        # Para el admin, incluimos todos los campos del usuario normal MÁS los roles y 'cantidad_asistencias'
        fields = ['nombre', 'apellido', 'rubro', 'rubro_otro', 'rut', 'email', 'telefono', 'password', 'foto', 'es_admin', 'es_ayudante', 'es_totem', 'cantidad_asistencias',
                  'nombre_empresa', 'descripcion_empresa', 'web_empresa', 'buscando'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'rubro': forms.Select(attrs={'class': 'form-select'}),
            'rubro_otro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escribe tu rubro aquí'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'es_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_ayudante': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_totem': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_empresa': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'web_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: miempresa.com'}),
            'buscando': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # self.instance es el objeto Usuario que se está editando.
        # Excluimos al propio usuario de la búsqueda de emails duplicados.
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo electrónico.")
        return email
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        is_valid, message_or_rut = validate_rut(rut)
        if not is_valid:
            raise forms.ValidationError(message_or_rut)
        if Usuario.objects.filter(rut=message_or_rut).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un usuario con este RUT.")
        return message_or_rut

    def clean(self):
        cleaned_data = super().clean()
        rubro = cleaned_data.get("rubro")
        rubro_otro = cleaned_data.get("rubro_otro")
        if rubro == 'otro' and not rubro_otro:
            self.add_error('rubro_otro', 'Debes especificar el rubro si seleccionas "Otro".')

    def save(self, commit=True):
        from django.contrib.auth.hashers import make_password
        usuario = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            usuario.password = make_password(password)
        if commit:
            usuario.save()
        return usuario


class AdminCrearUsuarioForm(AdminUsuarioForm):
    """
    Formulario para crear nuevos usuarios desde el panel admin.
    Requiere contraseña y no edita usuarios existentes.
    """
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa una contraseña'}),
        required=True,
        help_text="La contraseña debe tener al menos 8 caracteres."
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo electrónico.")
        return email

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        is_valid, message_or_rut = validate_rut(rut)
        if not is_valid:
            raise forms.ValidationError(message_or_rut)
        if Usuario.objects.filter(rut=message_or_rut).exists():
            raise forms.ValidationError("Ya existe un usuario con este RUT.")
        return message_or_rut

    def save(self, commit=True):
        from django.contrib.auth.hashers import make_password
        usuario = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            usuario.password = make_password(password)
        if commit:
            usuario.save()
        return usuario


class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(label="Contraseña Actual", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    nueva_password = forms.CharField(label="Nueva Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirmar_password = forms.CharField(label="Confirmar Nueva Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_nueva_password(self):
        password = self.cleaned_data.get('nueva_password')
        if len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        nueva_password = cleaned_data.get("nueva_password")
        confirmar_password = cleaned_data.get("confirmar_password")

        if nueva_password and confirmar_password and nueva_password != confirmar_password:
            self.add_error('confirmar_password', "Las nuevas contraseñas no coinciden.")
        return cleaned_data

class RespuestaEncuestaForm(forms.ModelForm):
    class Meta:
        model = RespuestaEncuesta
        fields = ['puntuacion', 'comentarios']
        widgets = {
            'puntuacion': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Tus comentarios son valiosos...'}),
        }
        labels = {
            'comentarios': 'Comentarios (opcional)'
        }
