from BAapp.models import Notificacion, MyUser

def crear_notificacion(
        titulo: str, 
        categoria: str, 
        hyperlink: str, 
        user: MyUser,
        descripcion: str = None 
    ):
    return Notificacion.objects.create(
        titulo=titulo,
        descripcion=descripcion,
        categoria=categoria,
        hyperlink=hyperlink,
        user=user,
    )