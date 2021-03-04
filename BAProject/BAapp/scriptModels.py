import datetime
from .forms import *
from .models import *
from .choices import *
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.http import HttpResponse
 
def loadModels(request):
    
    # Carga de Vendedores
    for a in range(5):
        user = User.objects.create_user('Juan'+str(a+1), 'juan'+str(a+1)+'@thebeatles.com', 'hola'+str(a+1))
        user.first_name = 'Juan'+str(a+1)
        user.last_name = 'Perez'+str(a+1)
        user.save()
        grupoVendedor = Group.objects.get(name='Vendedor') 
        grupoVendedor.user_set.add(user)
        t1, created = Telefono.objects.get_or_create(
            numero = 111111
         )
        fecha_nacimiento = datetime.date.today()
        p1, created = Persona.objects.get_or_create(
            user = user,
            dni = (10000000 + (a+1)),
            fecha_nacimiento = fecha_nacimiento,
            sexo = "HO",
            telefono = t1
         )   
        v, created = Vendedor.objects.get_or_create(
            persona = p1
     )
   

    empresa = Empresa.objects.get(pk=10)
    for a in range(5):
        user = User.objects.create_user('Lucia'+str(a+1), 'Lucia'+str(a+1)+'@thebeatles.com', 'Lucia'+str(a+1))
        user.first_name = 'Lucia'+str(a+1)
        user.last_name = 'Sanchez'+str(a+1)
        user.save()
        grupoProveedor = Group.objects.get(name='Proveedor') 
        grupoProveedor.user_set.add(user)
        t1, created = Telefono.objects.get_or_create(
            numero = 222222
        )
        fecha_nacimiento = datetime.date.today()
        p1, created = Persona.objects.get_or_create(
            user = user,
            dni = (20000000 + (a+1)),
            fecha_nacimiento = fecha_nacimiento,
            sexo = "MU",
            telefono = t1
        )
        #Si la idea es que cada Proovedor sea de una empresa diferente
        #empresa = Empresa.objects.get(pk=10+a)   
        p, created = Proveedor.objects.get_or_create(
            persona = p1,
            empresa = empresa
        )
    
    #Carga de Compradores
    #Todos trabajan para la misma Empresa.
    #empresa = Empresa.objects.get(pk=10)
    
    for a in range(5):
        user = User.objects.create_user('Diego'+str(a+1), 'Diego'+str(a+1)+'@thebeatles.com', 'Diego'+str(a+1))
        user.first_name = 'Diego'+str(a+1)
        user.last_name = 'Lopez'+str(a+1)
        user.save()
        grupoComprador = Group.objects.get(name='Comprador') 
        grupoComprador.user_set.add(user)
        t1, created = Telefono.objects.get_or_create(
            numero = 33333
        )
        fecha_nacimiento = datetime.date.today()
        p1, created = Persona.objects.get_or_create(
            user = user,
            dni = (30000000 + (a+1)),
            fecha_nacimiento = fecha_nacimiento,
            sexo = "HO",
            telefono = t1
        )
        #Si la idea es que cada Comprador sea de una empresa diferente
        empresa = Empresa.objects.get(pk=10+a)   
        c, created = Comprador.objects.get_or_create(
            persona = p1,
            empresa = empresa
        )

    #Carga de Gerentes
    #Todos trabajan para la misma Empresa.
    #empresa = Empresa.objects.get(pk=10)
  
    for a in range(5):
        user = User.objects.create_user('Steve'+str(a+1), 'Steve'+str(a+1)+'@thebeatles.com', 'Steve'+str(a+1))
        user.first_name = 'Steve'+str(a+1)
        user.last_name = 'Gates'+str(a+1)
        user.save()
        t1, created = Telefono.objects.get_or_create(
            numero = 444444
        )
        fecha_nacimiento = datetime.date.today()
        p1, created = Persona.objects.get_or_create(
            user = user,
            dni = (40000000 + (a+1)),
            fecha_nacimiento = fecha_nacimiento,
            sexo = "MU",
            telefono = t1
        )
        #Si la idea es que cada Gerente sea de una empresa diferente
        empresa = Empresa.objects.get(pk=10+a)   
        c, created = Gerente.objects.get_or_create(
            persona = p1,
            empresa = empresa
        )
    
    return HttpResponse("Creado")