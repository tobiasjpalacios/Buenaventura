from django import forms
from django.forms import ModelForm
from .models import *

class ProveedorForm(ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'

        widget = {
        	'Nombre' : forms.TextInput(attrs={'class':'form-control'}),
        	'Apellido' : forms.TextInput(attrs={'class':'form-control'}),
        	'Dni' : forms.TextInput(attrs={'class':'form-control'}),
        	'Email' : forms.TextInput(attrs={'class':'form-control'}),
        	'Fecha nacimiento' : forms.TextInput(attrs={'class':'form-control'}),
        	'Sexo' : forms.Select(),
        	'Telefono' : forms.TextInput(attrs={'class':'form-control'}),
        	'Codigo' : forms.TextInput(attrs={'class':'form-control'}),
        	'Fax' : forms.TextInput(attrs={'class':'form-control'}),
        	'Cuil cuit' : forms.TextInput(attrs={'class':'form-control'}),
        	'Codigo cta' : forms.TextInput(attrs={'class':'form-control'}),
        	'Saldo inicial' : forms.TextInput(attrs={'class':'form-control'}),
        	'Alicuota' : forms.TextInput(attrs={'class':'form-control'}),
        	'Desde iibb' : forms.TextInput(attrs={'class':'form-control'}),
        	'Hasta iibb' : forms.TextInput(attrs={'class':'form-control'}),
        	'Moneda' : forms.TextInput(attrs={'class':'form-control'}),
        	'Numero cai' : forms.TextInput(attrs={'class':'form-control'}),
        	'Vencimiento cai' : forms.TextInput(attrs={'class':'form-control'}),
        	'Observaciones' : forms.Textarea(attrs={'class':'form-control'}),
        }
