from django import forms
from django.forms import ModelForm
from .models import *
from .choices import *

class ProveedorForm(ModelForm):
    fecha_nacimiento = forms.DateTimeField(widget = forms.DateTimeInput(attrs={'class':'datepicker'}))
    vencimiento_cai = forms.DateTimeField(widget = forms.DateTimeInput(attrs={'class':'datepicker'}))
    class Meta:
        model = Proveedor
        fields = '__all__'

        widget = {
        'fecha_nacimiento' : forms.TextInput(attrs={'class':'datepicker'}),
        'vencimiento_cai' : forms.TextInput(attrs={'class':'vencimiento_cai'}),
    }


class ClienteForm(ModelForm):
    fecha_nacimiento = forms.DateTimeField(widget = forms.DateTimeInput(attrs={'class':'datepicker'}))
    class Meta:
        model = Cliente
        fields = '__all__'

        widget = {
            'fecha_nacimiento' : forms.TextInput(attrs={'class':'datepicker'}),
        }

