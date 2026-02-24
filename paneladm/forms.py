from django import forms
from .models import Reunion, Encuesta, SoporteTicket, TicketRespuesta

class ReunionForm(forms.ModelForm):
    class Meta:
        model = Reunion
        fields = ['detalle', 'descripcion', 'fecha', 'ubicacion', 'imagen', 'imprimir_etiqueta_al_asistir']
        widgets = {
            'detalle': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'imprimir_etiqueta_al_asistir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            # Ocultamos el texto de ayuda por defecto para manejarlo en la plantilla
            'imprimir_etiqueta_al_asistir': None,
        }

class EncuestaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        reuniones_con_encuesta = Encuesta.objects.values_list('reunion_id', flat=True)
        self.fields['reunion'].queryset = Reunion.objects.exclude(id__in=reuniones_con_encuesta)

    class Meta:
        model = Encuesta
        fields = ['reunion', 'titulo', 'activa']
        widgets = {
            'reunion': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SoporteTicketForm(forms.ModelForm):
    class Meta:
        model = SoporteTicket
        fields = ['asunto', 'mensaje']
        widgets = {
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Problema al editar mi perfil'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe tu problema o consulta con el mayor detalle posible.'}),
        }

class SoporteTicketAdminForm(forms.ModelForm):
    class Meta:
        model = SoporteTicket
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class TicketRespuestaForm(forms.ModelForm):
    class Meta:
        model = TicketRespuesta
        fields = ['mensaje', 'imagen']
        widgets = {
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Escribe tu respuesta...'}),
            'imagen': forms.FileInput(attrs={'class': 'd-none'}),
        }
        labels = {
            'mensaje': ''
        }