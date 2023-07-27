# Generated by Django 3.1.2 on 2023-01-21 00:23

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Articulo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca', models.CharField(max_length=50)),
                ('ingrediente', models.CharField(max_length=200)),
                ('concentracion', models.CharField(max_length=50, null=True)),
                ('banda_toxicologica', models.CharField(choices=[('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV'), ('LA', 'LA'), ('LB', 'LB')], max_length=50, null=True)),
                ('descripcion', models.CharField(blank=True, max_length=50, null=True)),
                ('unidad', models.CharField(max_length=50, null=True)),
                ('formulacion', models.CharField(max_length=20, null=True)),
            ],
            options={
                'search_fields': ('marca', 'ingrediente', 'concentracion'),
            },
        ),
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('razon_social', models.CharField(max_length=50, unique=True)),
                ('nombre_comercial', models.CharField(blank=True, max_length=50, null=True)),
                ('cuit', models.CharField(blank=True, max_length=14, null=True)),
                ('ingresos_brutos', models.CharField(blank=True, max_length=255, null=True)),
                ('fecha_exclusion', models.DateField(blank=True, null=True)),
                ('categoria_iva', models.CharField(blank=True, choices=[('EX', 'Exento'), ('RIM', 'Responsable Inscripto M'), ('RI', 'Responsable Inscripto'), ('MO', 'Monotributo'), ('CF', 'Consumidor Final')], max_length=25, null=True)),
                ('domicilio_fiscal', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'search_fields': ('razon_social', 'nombre_comercial', 'cuit', 'categoria_iva'),
            },
        ),
        migrations.CreateModel(
            name='Factura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField()),
                ('fecha_vencimiento', models.DateField()),
                ('numero_factura', models.IntegerField()),
                ('monto', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99999999)])),
                ('documento', models.FileField(upload_to='media/facturas/%Y/%m/%d')),
            ],
            options={
                'default_related_name': 'facturas',
            },
        ),
        migrations.CreateModel(
            name='Financiacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condicion', models.BooleanField()),
                ('tasa', models.IntegerField(null=True)),
                ('condicion_comercial', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Negocio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('fecha_cierre', models.DateTimeField(blank=True, null=True)),
                ('tipo_de_negocio', models.CharField(choices=[('VT', 'Venta'), ('CS', 'Consignacion')], max_length=2)),
                ('aprobado', models.BooleanField(default=False)),
                ('cancelado', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Retencion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TipoPago',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30)),
                ('descripcion', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('clase', models.CharField(choices=[('Administrador', 'Administrador'), ('Comprador', 'Comprador'), ('Vendedor', 'Vendedor'), ('Proveedor', 'Proveedor'), ('Gerente', 'Gerente'), ('Logistica', 'Logistica')], max_length=13, null=True)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('sexo', models.CharField(blank=True, choices=[('HO', 'Hombre'), ('MU', 'Mujer'), ('NB', 'Otro')], max_length=6, null=True)),
                ('dni', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99999999)])),
                ('telefono', models.CharField(blank=True, max_length=10, null=True)),
                ('domicilio', models.CharField(blank=True, max_length=255, null=True)),
                ('is_superuser', models.BooleanField(default=True, help_text='Puede loggearse en el administrador y dar permisos a otros usuarios.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Puede loggearse en el administrador.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Quitar este parámetro en lugar de borrar cuentas', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='BAapp.empresa')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Usuario',
                'verbose_name_plural': 'Usuarios',
            },
        ),
        migrations.CreateModel(
            name='Remito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField()),
                ('fecha_vencimiento', models.DateField()),
                ('lote', models.CharField(max_length=255)),
                ('observaciones', models.TextField()),
                ('documento', models.FileField(upload_to='media/remitos/%Y/%m/%d')),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='remitos', to='BAapp.negocio')),
                ('proveedor', models.ForeignKey(limit_choices_to={'clase': 'Proveedor'}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='remitos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_related_name': 'remitos',
            },
        ),
        migrations.CreateModel(
            name='Recibo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField()),
                ('monto', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99999999)])),
                ('documento', models.FileField(upload_to='media/recibos/%Y/%m/%d')),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='BAapp.negocio')),
                ('recibe_proveedor', models.ForeignKey(limit_choices_to={'clase': 'Proveedor'}, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Propuesta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observaciones', models.CharField(blank=True, max_length=300)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('envio_comprador', models.BooleanField()),
                ('visto', models.BooleanField(default=False)),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='propuestas', to='BAapp.negocio')),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
        migrations.CreateModel(
            name='Presupuesto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(max_length=50)),
                ('fecha', models.DateField(auto_now_add=True)),
                ('cobrado', models.BooleanField(default=False)),
                ('observaciones', models.CharField(max_length=300)),
                ('visualizacion', models.BooleanField()),
                ('propuesta', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='BAapp.propuesta')),
            ],
        ),
        migrations.CreateModel(
            name='OrdenDePago',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField()),
                ('monto', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99999999)])),
                ('documento', models.FileField(upload_to='media/ordenesPagos/%Y/%m/%d')),
                ('factura', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='BAapp.factura')),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='BAapp.negocio')),
                ('recibe_proveedor', models.ForeignKey(limit_choices_to={'clase': 'Proveedor'}, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrdenDeCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField()),
                ('documento', models.FileField(upload_to='media/ordenesCompras/%Y/%m/%d')),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='BAapp.negocio')),
                ('recibe_proveedor', models.ForeignKey(limit_choices_to={'clase': 'Proveedor'}, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('descripcion', models.CharField(blank=True, max_length=255, null=True)),
                ('categoria', models.CharField(max_length=64)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('hyperlink', models.CharField(max_length=255)),
                ('visto', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='Nota',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField()),
                ('tipo_nota', models.CharField(choices=[('CR', 'Credito'), ('DV', 'Débito')], max_length=15)),
                ('documento', models.FileField(upload_to='media/notas/%Y/%m/%d')),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='notas', to='BAapp.negocio')),
            ],
            options={
                'default_related_name': 'notas',
            },
        ),
        migrations.AddField(
            model_name='negocio',
            name='comprador',
            field=models.ForeignKey(limit_choices_to={'clase': 'Comprador'}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='comprador', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='negocio',
            name='vendedor',
            field=models.ForeignKey(limit_choices_to={'clase': 'Vendedor'}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='vendedor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ItemPropuesta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(blank=True, null=True)),
                ('precio_venta', models.FloatField(blank=True, null=True)),
                ('precio_compra', models.FloatField(blank=True, null=True)),
                ('divisa', models.CharField(blank=True, choices=[('AR', 'Pesos'), ('USD', 'Dolar')], max_length=40, null=True)),
                ('destino', models.CharField(default='', max_length=255, null=True)),
                ('fecha_entrega', models.CharField(blank=True, max_length=12, null=True)),
                ('aceptado', models.BooleanField()),
                ('pagado', models.BooleanField(default=False)),
                ('fecha_pago', models.CharField(blank=True, max_length=12, null=True)),
                ('fecha_real_pago', models.DateTimeField(blank=True, null=True)),
                ('tasa', models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=4, null=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
                ('fecha_salida_entrega', models.DateTimeField(blank=True, null=True)),
                ('fecha_real_entrega', models.DateTimeField(blank=True, null=True)),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='BAapp.articulo')),
                ('propuesta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='BAapp.propuesta')),
                ('proveedor', models.ForeignKey(blank=True, limit_choices_to={'clase': 'Proveedor'}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('tipo_pago', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='BAapp.tipopago')),
            ],
        ),
        migrations.CreateModel(
            name='FacturaComision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField()),
                ('documento', models.FileField(upload_to='media/facturasComision/%Y/%m/%d')),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='facturas_comisiones', to='BAapp.negocio')),
                ('recibe_proveedor', models.ForeignKey(limit_choices_to={'clase': 'Proveedor'}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='facturas_comisiones', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_related_name': 'facturas_comisiones',
            },
        ),
        migrations.AddField(
            model_name='factura',
            name='negocio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='facturas', to='BAapp.negocio'),
        ),
        migrations.AddField(
            model_name='factura',
            name='proveedor',
            field=models.ForeignKey(limit_choices_to={'clase': 'Proveedor'}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='facturas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='factura',
            name='tipo_pago',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='facturas', to='BAapp.tipopago'),
        ),
        migrations.AddField(
            model_name='empresa',
            name='retenciones',
            field=models.ManyToManyField(blank=True, to='BAapp.Retencion'),
        ),
        migrations.CreateModel(
            name='CuentaCorriente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField()),
                ('documento', models.FileField(upload_to='media/cuentasCorriente/%Y/%m/%d')),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='cuentas_corrientes', to='BAapp.negocio')),
            ],
            options={
                'default_related_name': 'cuentas_corrientes',
            },
        ),
        migrations.CreateModel(
            name='ConstanciaRentencion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField()),
                ('importe', models.FloatField()),
                ('documento', models.FileField(upload_to='media/constanciasRetencion/%Y/%m/%d')),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='BAapp.negocio')),
                ('recibe_proveedor', models.ForeignKey(limit_choices_to={'clase': 'Proveedor'}, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cheque',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateField()),
                ('documento', models.FileField(upload_to='media/cheques/%Y/%m/%d')),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='cheques', to='BAapp.negocio')),
            ],
            options={
                'default_related_name': 'cheques',
            },
        ),
        migrations.AddField(
            model_name='articulo',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='articulos', to='BAapp.empresa'),
        ),
    ]
