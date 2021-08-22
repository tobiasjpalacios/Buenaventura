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
    
class FacturaForm(forms.ModelForm):

    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())    
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    fecha_vencimiento = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker2'}))
    documento = forms.FileInput()


    class Meta:
        model = Factura
        fields = '__all__'

class RemitoForm(forms.ModelForm):

    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())    
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    fecha_vencimiento = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    documento = forms.FileInput()
    
    class Meta:
        model = Remito
        fields = '__all__'

class OrdenDeCompraForm(forms.ModelForm):

    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())    
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    documento = forms.FileInput()
    
    class Meta:
        model = OrdenDeCompra
        fields = '__all__'

class OrdenDePagoForm(forms.ModelForm):

    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())    
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    documento = forms.FileInput()
    
    class Meta:
        model = OrdenDePago
        fields = '__all__'

class ConstanciaRentencionForm(forms.ModelForm):

    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())    
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    documento = forms.FileInput()
    
    class Meta:
        model = ConstanciaRentencion
        fields = '__all__'

class ReciboForm(forms.ModelForm):

    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())    
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    documento = forms.FileInput()
    
    class Meta:
        model = Recibo
        fields = '__all__'

class ChequesForm(forms.ModelForm):

    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    documento = forms.FileInput()


    class Meta:
        model = Cheque
        fields = '__all__'
        #exclude = ('negocio',)

class CuentaCorrientesForm(forms.ModelForm):

    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())    
    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    documento = forms.FileInput()
    
    class Meta:
        model = CuentaCorriente
        fields = '__all__'

class FacturaComisionesForm(forms.ModelForm):

    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())    
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    documento = forms.FileInput()
    
    class Meta:
        model = FacturaComision
        fields = '__all__'

class NotaForm(forms.ModelForm):

    negocio = forms.ModelChoiceField(queryset=Negocio.objects.all(), widget=forms.HiddenInput())    
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}))
    documento = forms.FileInput()
    
    class Meta:
        model = Nota
        fields = '__all__'
