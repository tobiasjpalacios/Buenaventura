from django import forms
from django.forms import ModelForm
from .models import *
from .choices import *

class ProveedorForm(ModelForm):
    fecha_nacimiento = forms.DateField(widget = forms.DateInput(attrs={'class':'datepicker'}))
    vencimiento_cai = forms.DateField(widget = forms.DateInput(attrs={'class':'datepicker'}))
    class Meta:
        model = Proveedor
        fields = '__all__'

        widget = {
        'fecha_nacimiento' : forms.TextInput(attrs={'class':'datepicker'}),
        'vencimiento_cai' : forms.TextInput(attrs={'class':'vencimiento_cai'}),
    }


class ClienteForm(ModelForm):
    fecha_nacimiento = forms.DateField(widget = forms.DateInput(attrs={'class':'datepicker'}))

    class Meta:
        model = Cliente
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
    mes_de_pago = forms.DateField(widget = forms.DateInput(attrs={'class':'datepicker'}))

    class Meta:
        model = Presupuesto
        fields = '__all__'


        widget = {
            'fecha' : forms.TextInput(attrs={'class':'datepicker'}),
            'fecha_de_pago' : forms.TextInput(attrs={'class':'datepicker'}),
        }

class PropuestaForm(ModelForm):
    fecha_entrega = forms.DateField(widget = forms.DateInput(attrs={'class':'datepicker'}))
    fecha_creacion = forms.DateField(widget = forms.DateInput(attrs={'class':'datepicker'}))

    class Meta:
        model = Propuesta
        fields = '__all__'


        widget = {
            'fecha_entrega' : forms.TextInput(attrs={'class':'datepicker'}),
            'fecha_creacion' : forms.TextInput(attrs={'class':'datepicker'}),
        }