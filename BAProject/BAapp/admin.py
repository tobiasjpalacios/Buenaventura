from django.contrib import admin
from .models import *


from django.contrib.auth.models import User, Group
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import (
    AdminPasswordChangeForm, UserChangeForm, UserCreationForm,
)
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.db import router, transaction
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay
import json
from django.contrib.auth.forms import *
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import redirect
from datetime import datetime


class ItemPropuestaInline(admin.TabularInline):
    model = ItemPropuesta
    extra = 1

class PropuestaAdmin(admin.ModelAdmin):
    inlines = (ItemPropuestaInline,)

class ArticuloAdmin(admin.ModelAdmin):
    # inlines = (ItemPropuestaInline,)
    list_filter = ('banda_toxicologica', 'marca', 'empresa')
    list_display = ('ingrediente', 'marca','empresa',)
    search_fields = ['ingrediente', 'marca','empresa__razon_social', ]
    ordering = ["ingrediente"]

class FacturaAdmin(admin.ModelAdmin):
    list_display  = ('fecha_emision','documento')

class NegocioAdmin(admin.ModelAdmin):
    list_display = ('id_de_neg', 'fecha_cierre')


csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())

admin.site.index_title = _("Bv")
admin.site.site_header = _("Buenaventura")
admin.site.site_title = _("Buenaventura")

class MyUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ()

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(MyUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class MyUserAdmin(UserAdmin):
    list_display = ('email', 'active', 'admin')
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('nombre','apellido','email', 'password')}),
        (_('Datos Personales'), {'fields': ('empresa','fecha_nacimiento', 'sexo', 'dni', 'telefono','domicilio')}),
        (_('Permisos'), {
            'fields': ('clase', 'is_active', 'is_staff', 'is_superuser', 'groups'),
        }),
        (_('Fechas importantes'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nombre','apellido','email', 'password1', 'password2', 'clase'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['nivel']
        else:
            return []

    form = UserChangeForm
    add_form = MyUserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('email', 'is_staff')
    list_filter = ('is_active',)
    search_fields = ('email',)
    ordering = ('email',)



    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_urls(self):
        return [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.user_change_password),
                name='auth_user_password_change',
            ),
        ] + super().get_urls()

    def lookup_allowed(self, lookup, value):
        # Don't allow lookups involving passwords.
        return not lookup.startswith('password') and super().lookup_allowed(lookup, value)

    @sensitive_post_parameters_m
    @csrf_protect_m
    def add_view(self, request, form_url='', extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._add_view(request, form_url, extra_context)

    def _add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super().add_view(request, form_url, extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        user = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = gettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determine the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST = request.POST.copy()
            request.POST['_continue'] = 1
        return super().response_add(request, obj, post_url_continue)

class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'nombre_comercial', 'cuit','categoria_iva')
    list_filter = ('categoria_iva',)
    search_fields = ['razon_social','nombre_comercial','cuit', ]
    ordering = ["nombre_comercial"]

admin.site.unregister(Group)
admin.site.register(MyUser, MyUserAdmin)


admin.site.register(Articulo, ArticuloAdmin)
admin.site.register(Presupuesto)
admin.site.register(Propuesta, PropuestaAdmin)
admin.site.register(Empresa, EmpresaAdmin)

admin.site.register(Retencion)
admin.site.register(ItemPropuesta)
admin.site.register(Financiacion)
admin.site.register(Negocio, NegocioAdmin)
admin.site.register(TipoPago)
admin.site.register(Notificacion)
admin.site.register(Factura, FacturaAdmin)
admin.site.register(Remito)
admin.site.register(OrdenDeCompra)
admin.site.register(OrdenDePago)
admin.site.register(ConstanciaRentencion)
admin.site.register(Recibo)
admin.site.register(Cheque)
admin.site.register(CuentaCorriente)
admin.site.register(FacturaComision)
admin.site.register(Nota)