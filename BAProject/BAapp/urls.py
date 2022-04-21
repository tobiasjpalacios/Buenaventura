from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from BAapp.views import *
from django.contrib.auth.decorators import login_required

apipatters = [
    path('articulos/',APIArticulos.as_view() , name="api_articulos"),
    path('compradores/',APIComprador.as_view() , name="api_comprador"),
    path('vendedores/',APIVendedor.as_view() , name="api_vendedor"),
    path('distribuidor/',APIDistribuidor.as_view() , name="api_distribuidor"),
    path('empresa/',APIEmpresa.as_view() , name="api_empresa"),
]

urlpatterns = [
    path('', landing_page, name='home'),
    path('administrar/', admin, name="admin"),
    path('testeo/', testeo, name="testeo"),
    path('chat/', chat, name="chat"),
    path('inicio/', inicio, name="inicio"),
    path('cliente/', cliente, name="Cliente"),
    path('createAlertaNV/', createAlertaNV, name="createAlertaNV"),
    path('password/',PasswordsChangeView.as_view(template_name="tempAux/changePassword.html")),
    path('successPassword/', successPassword, name="successPassword"),
    path('vendedor/', vendedor, name="vendedor"),
    path('router/', check_user_group_after_login, name="router"),
    path('vistaAdministrador/', vistaAdministrador, name="vistaAdministrador"),
    path('vistaLogistica/', vistaLogistica, name="vistaLogistica"),
    path('vistaProveedor/', vistaProveedor, name="vistaProveedor"),
    path('vistaGerente/', vistaGerente, name="vistaGerente"),
    path('vistaCliente/', vistaCliente, name="vistaCliente"),
    path('detalleAlerta/', detalleAlerta, name="detalleAlerta"),
    path('detalleLogistica/', detalleLogistica, name="detalleLogistica"),
    path('detalleNegocio/', detalleNegocio, name="detalleNegocio"),
    path('detalleNotis/', detalleNotis, name="detalleNotis"),
    path('detalleItem/', detalleItem, name="detalleItem"),
    path('sendAlertaLog/', sendAlertaLog, name="sendAlertaLog"),
    path('reloadLog/', reloadLog, name="reloadLog"),
    path('sendAlertaModal/', sendAlertaModal, name="sendAlertaModal"),
    path('setLogistica/', setLogistica, name="setLogistica"),
    path('detalleSemaforo/', detalleSemaforo, name="detalleSemaforo"),
    path('setFechaPagoReal/', setFechaPagoReal, name="setFechaPagoReal"),
    path('reloadSem/', reloadSem, name="reloadSem"),   
    path('carga_excel/', carga_excel.as_view(), name="carga_excel"),
    path('filtrarNegocios/', filtrarNegocios, name ="filtrarNegocios"),
    path('todosFiltro/<tipo>', todosFiltro, name='todosFiltro'),
    path('cuentas/', cuentas, name="cuentas"),


    #nuevas urls
    path('notificaciones/', login_required(login_url='/', redirect_field_name='router')(NotificacionesView.as_view()), name ="notificaciones"),
    path('presupuestos/', login_required(login_url='/', redirect_field_name='router')(PresupuestosView.as_view()), name="presupuestos"),
    path('todos_negocios/', login_required(login_url='/', redirect_field_name='router')(TodoseNegociosView.as_view()), name ="todos_negocios"),
    path('logistica/', login_required(login_url='/', redirect_field_name='router')(LogisticaView.as_view()), name ="logistica"),
    path('vencimientos/', login_required(login_url='/', redirect_field_name='router')(VencimientosView.as_view()), name ="vencimientos"),
    path('info_negocio/<int:pk>', login_required(login_url='/', redirect_field_name='router')(Info_negocioView.as_view()), name ="info_negocio"),    
    path('comprobantes/', login_required(login_url='/', redirect_field_name='router')(ComprobantesView.as_view()), name ="comprobantes"),



    path('compradores/', ListCompradorView.as_view(), name="mostrar_compradores"),
    path('comprador/<int:pk>', CompradorView.as_view(), name="comprador"),
    path('comprador/', CompradorView.as_view(), name="registrar_comprador"),
        
    path('proveedores/', ListProveedorView.as_view(), name = "mostrar_proveedores"),
    path('proveedor/<int:pk>', ProveedorView.as_view(), name="proveedor"),
    path('proveedor/', ProveedorView.as_view(), name="crear_proveedor"),

    path('articulos/', ListArticuloView.as_view(), name = "mostrar_articulos"),
    path('articulo/<int:pk>', ArticuloView.as_view(), name="articulo"),
    path('articulo/', ArticuloView.as_view(), name="crear_articulo"),

    path('presupuestosO/', ListPresupuestoView.as_view(), name = "mostrar_presupuestos"),
    path('presupuesto/<int:pk>', PresupuestoView.as_view(), name="presupuesto"),
    path('presupuesto/', PresupuestoView.as_view(), name="crear_presupuesto"),

    #path('propuesta/', ListPropuestaView.as_view(), name = "mostrar_propuestas"),
    path('propuesta/<int:pk>', PropuestaView.as_view(), name="propuesta"),
    path('propuesta/', PropuestaView.as_view(), name="crear_propuesta"),

    #path('propuesta/', ListPropuestaView.as_view(), name = "mostrar_propuestas"),
    path('negocio/<int:pk>', login_required(login_url='/', redirect_field_name='router')(NegocioView.as_view()), name="negocio"),
    path('negocio/', login_required(login_url='/', redirect_field_name='router')(NegocioView.as_view()), name="crear_negocio"),

    path('empresas/', ListEmpresaView.as_view(), name = "mostrar_empresas"),
    path('empresa/<int:pk>', EmpresaView.as_view(), name="empresa"),
    path('empresa/', EmpresaView.as_view(), name="registrar_empresa"),

    # crear propuestas

    path('api/', include(apipatters)),
    path('filterArticulo/<str:ingrediente>', filterArticulo, name="filterArticulo"),
    path('getPagos/', getPagos, name="getPagos"),

    #crear comprobantes

    path('selecNegComprobante/<tipo>', selecNegComprobante, name="selecNegComprobante"),


    path('formFactura/<neg>', formFactura, name="formFactura"),
    path('formFactura/', formFactura, name="formFactura"),
    
    path('formRemito/<neg>', formRemito, name="formRemito"),
    path('formRemito/', formRemito, name="formRemito"),
    
    path('formOrdenDeCompra/<neg>', formOrdenDeCompra, name="formOrdenDeCompra"),
    path('formOrdenDeCompra/', formOrdenDeCompra, name="formOrdenDeCompra"),
    
    path('formOrdenDePago/<neg>', formOrdenDePago, name="formOrdenDePago"),
    path('formOrdenDePago/', formOrdenDePago, name="formOrdenDePago"),
    
    path('formConstanciaRentencion/<neg>', formConstanciaRentencion, name="formConstanciaRentencion"),
    path('formConstanciaRentencion/', formConstanciaRentencion, name="formConstanciaRentencion"),

    path('formRecibo/<neg>', formRecibo, name="formRecibo"),
    path('formRecibo/', formRecibo, name="formRecibo"),
    
    path('formCheque/<neg>', formCheque, name="formChequeDef"),
    path('formCheque/', formCheque, name="formCheque"),
    

    path('formCuentaCorriente/<neg>', formCuentaCorriente, name="formCuentaCorriente"),
    path('formCuentaCorriente/', formCuentaCorriente, name="formCuentaCorriente"),
    
    path('formFacturaComision/<neg>', formFacturaComision, name="formFacturaComision"),
    path('formFacturaComision/', formFacturaComision, name="formFacturaComision"),
    
    path('formNota/<neg>', formNota, name="formNota"),
    path('formNota/', formNota, name="formNota"),


]
