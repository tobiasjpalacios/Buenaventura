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
    # path('testeo/', testeo, name="testeo"),
    path('chat/', chat, name="chat"),
    path('cliente/', cliente, name="Cliente"),
    path('password/',PasswordsChangeView.as_view(template_name="tempAux/changePassword.html")),
    path('success-password/', successPassword, name="successPassword"),
    path('detalle-alerta/', detalleAlerta, name="detalleAlerta"),
    path('detalle-negocio/', detalleNegocio, name="detalleNegocio"),
    path('detalle-notis/', detalleNotis, name="detalleNotis"),
    path('detalle-item/', detalleItem, name="detalleItem"),
    path('send-alerta-modal/', sendAlertaModal, name="sendAlertaModal"), 
    path('carga-excel/', login_required(login_url='/')(carga_excel.as_view()), name="carga_excel"),
    path('descarga-db-excel/', login_required(login_url='/')(descarga_db_excel), name="descarga_db_excel"),
    path('filtrar-negocios/', filtrarNegocios, name ="filtrarNegocios"),
    path('todos-filtro/<tipo>', todosFiltro, name='todosFiltro'),
    path('cuentas/', cuentas, name="cuentas"),
    path('redirect-hyperlink/<int:id>', notisHyperlinkRedirect, name='redirect_hyperlink'),


    #nuevas urls
    path('inicio/', login_required(login_url='/')(Inicio.as_view()), name="inicio"),
    path('nuevo-negocio/', login_required(login_url='/')(NuevoNegocioView.as_view()), name="nuevo_negocio"),
    path('notificaciones/', login_required(login_url='/')(NotificacionesView.as_view()), name ="notificaciones"),
    path('presupuestos/', login_required(login_url='/')(PresupuestosView.as_view()), name="presupuestos"),
    path('todos-negocios/', login_required(login_url='/')(TodoseNegociosView.as_view()), name ="todos_negocios"),
    path('logistica/', login_required(login_url='/')(LogisticaView.as_view()), name ="logistica"),
    path('vencimientos/', login_required(login_url='/')(VencimientosView.as_view()), name ="vencimientos"),
    path('info-negocio/<int:pk>', login_required(login_url='/')(Info_negocioView.as_view()), name ="info_negocio"),    
    path('menu-comprobantes/', login_required(login_url='/')(MenuComprobantesView.as_view()), name ="menu_comprobantes"),
    path('comprobantes/', login_required(login_url='/')(ComprobantesView.as_view()), name ="comprobantes"),


    path('facturas/', login_required(login_url='/')(ComprobantesView.as_view()), name ="facturas"),
    path('remitos/', login_required(login_url='/')(ComprobantesView.as_view()), name ="remitos"),
    path('ordenes-compras/', login_required(login_url='/')(ComprobantesView.as_view()), name ="ordenesCompras"),
    path('ordenes-pagos/', login_required(login_url='/')(ComprobantesView.as_view()), name ="ordenesPagos"),
    path('contancias/', login_required(login_url='/')(ComprobantesView.as_view()), name ="contancias"),
    path('recibos/', login_required(login_url='/')(ComprobantesView.as_view()), name ="recibos"),
    path('cheques/', login_required(login_url='/')(ComprobantesView.as_view()), name ="cheques"),
    path('cuentas-corrientes/', login_required(login_url='/')(ComprobantesView.as_view()), name ="cuentasCorrientes"),
    path('facturas-comision/', login_required(login_url='/')(ComprobantesView.as_view()), name ="facturasComision"),
    path('notas/', login_required(login_url='/')(ComprobantesView.as_view()), name ="notas"),
    path('generar-pdf/', generar_pdf, name="generar_pdf"),


    path('articulos/', ListArticuloView.as_view(), name = "mostrar_articulos"),
    path('articulo/<int:pk>', ArticuloView.as_view(), name="articulo"),
    path('articulo/', ArticuloView.as_view(), name="crear_articulo"),

    path('presupuestosO/', ListPresupuestoView.as_view(), name = "mostrar_presupuestos"),
    path('presupuesto/<int:pk>', PresupuestoView.as_view(), name="presupuesto"),
    path('presupuesto/', PresupuestoView.as_view(), name="crear_presupuesto"),

    path('negocio/<int:id_de_neg>', login_required(login_url='/')(NegocioView.as_view()), name="negocio"),
    path('negocio/', login_required(login_url='/')(NegocioView.as_view()), name="crear_negocio"),

    path('empresas/', ListEmpresaView.as_view(), name = "mostrar_empresas"),
    path('empresa/<int:pk>', EmpresaView.as_view(), name="empresa"),
    path('empresa/', EmpresaView.as_view(), name="registrar_empresa"),

    # crear propuestas

    path('api/', include(apipatters)),
    path('filter-articulo/<str:word>', filterArticulo, name="filterArticulo"),
    path('get-pagos/', getPagos, name="getPagos"),

    #crear comprobantes

    path('selec-neg-comprobante/<tipo>', selecNegComprobante, name="selecNegComprobante"),

    path('form-factura/<neg>', formFactura, name="formFactura"),
    path('form-factura/', formFactura, name="formFactura"),
    
    path('form-remito/<neg>', formRemito, name="formRemito"),
    path('form-remito/', formRemito, name="formRemito"),
    
    path('form-orden-de-compra/<neg>', formOrdenDeCompra, name="formOrdenDeCompra"),
    path('form-orden-de-compra/', formOrdenDeCompra, name="formOrdenDeCompra"),
    
    path('form-orden-de-pago/<neg>', formOrdenDePago, name="formOrdenDePago"),
    path('form-orden-de-pago/', formOrdenDePago, name="formOrdenDePago"),
    
    path('form-constancia-rentencion/<neg>', formConstanciaRentencion, name="formConstanciaRentencion"),
    path('form-constancia-rentencion/', formConstanciaRentencion, name="formConstanciaRentencion"),

    path('form-recibo/<neg>', formRecibo, name="formRecibo"),
    path('form-recibo/', formRecibo, name="formRecibo"),
    
    path('form-cheque/<neg>', formCheque, name="formChequeDef"),
    path('form-cheque/', formCheque, name="formCheque"),
    

    path('form-cuenta-corriente/<neg>', formCuentaCorriente, name="formCuentaCorriente"),
    path('form-cuenta-corriente/', formCuentaCorriente, name="formCuentaCorriente"),
    
    path('form-factura-comision/<neg>', formFacturaComision, name="formFacturaComision"),
    path('form-factura-comision/', formFacturaComision, name="formFacturaComision"),
    
    path('form-nota/<neg>', formNota, name="formNota"),
    path('form-nota/', formNota, name="formNota"),


]
