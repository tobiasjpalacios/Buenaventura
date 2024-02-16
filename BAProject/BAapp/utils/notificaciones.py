import re
from BAapp.models import Notificacion

def modify_titulo_for_comprador(original_titulo, compador_name):
    pattern = r" de " + re.escape(compador_name)
    if compador_name in original_titulo:
        modified_titulo = re.sub(pattern, "", original_titulo)
    else:
        modified_titulo = original_titulo
    return modified_titulo

def crear_notificacion(context: dict):
    """
    context = {
        "titulo": str, 
        "descripcion": str | None,
        "categoria": str, 
        "hyperlink": str, 
        "user": MyUser
    }
    """
    try:
        titulo, categoria, hyperlink, user = context['titulo'], context['categoria'], context['hyperlink'], context['user']
        descripcion = context.get("descripcion", None)
    except KeyError:
        categoria = None
    return Notificacion.objects.create(
        titulo=titulo,
        descripcion=descripcion,
        categoria=categoria,
        hyperlink=hyperlink,
        user=user,
    )
    
def crear_notificaciones_usuarios(users_list: list, context: dict):
    """
    users_list = [MyUser Object 1, MyUser Object 2, ...]
    
    context = {
        "titulo": str, 
        "descripcion": str | None,
        "categoria": str, 
        "hyperlink": str
    }
    """
    for user in users_list:
        tmp_context = context.copy()
        tmp_context["user"] = user
        tmp_context["titulo"] = modify_titulo_for_comprador(tmp_context["titulo"], user.get_full_name())
        crear_notificacion(tmp_context)