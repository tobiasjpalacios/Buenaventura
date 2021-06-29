from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordChangeForm, User
from .models import *
from .choices import *

class ProveedorForm(ModelForm):
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    class Meta:
        model = Proveedor
        fields = '__all__'

        widget = {
        'fecha_nacimiento': forms.TextInput(attrs={'class':'datepicker'}),
    }


class CompradorForm(ModelForm):
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))

    class Meta:
        model = Comprador
        fields = '__all__'

        widget = {
            'fecha_nacimiento' : forms.TextInput(attrs={'class':'datepicker'}),
        }

class ArticuloForm(ModelForm):

    class Meta:
        model = Articulo
        fields = '__all__'

class PresupuestoForm(ModelForm):
    fecha = forms.DateField(widget = forms.DateInput(attrs={'class':'datepicker'}))
    class Meta:
        model = Presupuesto
        fields = '__all__'


        widget = {
            'fecha': forms.TextInput(attrs={'class':'datepicker'}),
        }

class PropuestaForm(ModelForm):
    fecha_entrega = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    fecha_creacion = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))

    class Meta:
        model = Propuesta
        fields = '__all__'


        widget = {
            'fecha_entrega': forms.TextInput(attrs={'class':'datepicker'}),
            'fecha_creacion': forms.TextInput(attrs={'class':'datepicker'}),
        }

class EmpresaForm(ModelForm):
    fecha_exclusion = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    exlusion_ret = forms.BooleanField(required=False, label="Exlusion ret")

    class Meta:
        model = Empresa
        fields = '__all__'


        widget = {
            'fecha_exclusion': forms.TextInput(attrs={'class':'datepicker'}),
        }

class PasswordsChangingForm(PasswordChangeForm):
    old_password = forms.TextInput()
    new_password1 = forms.TextInput()
    new_password2 = forms.TextInput()

    class Meta:
        model = User
        fields = ('old_password','new_password1','new_password2')
    
        