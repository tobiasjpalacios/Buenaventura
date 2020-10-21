from django.forms import ModelForm
from .models import *

class ProveedorForm(ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'

        
