from django.conf import settings
from django.contrib import admin
from django.contrib.admin import StackedInline
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from core import models


@admin.register(models.User)
class UserAdmin(UserAdmin):
    list_display = ('email', 'name', 'is_active', 'is_staff', 'is_superuser',)
    list_filter = ('is_active', 'is_staff', 'is_superuser',)
    search_fields = ('email', 'name',)
    ordering = ('name',)

    fieldsets = (
        (None, {'fields': ('name', 'email', 'password')}),
        (_(u'Permissões'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',)}),
        (_(u'Datas importantes'), {'fields': ('date_joined', 'created_at', 'updated_at',)}),
    )

    readonly_fields = ('date_joined', 'created_at', 'updated_at',)


# Disativar o modelo Grupo padrão do Django
admin.site.unregister(Group)


@admin.register(models.Perfil)
class ProfileAdmin(GroupAdmin):
    def changelist_view(self, request, extra_context=None):
        for name in ('Administrador', 'Anunciante',):
            Group.objects.get_or_create(name=name)
        return super().changelist_view(request, extra_context)


class EnderecoInline(StackedInline):
    model = models.Endereco
    max_num = 1
    extra = 0
    verbose_name = verbose_name_plural = _('Endereço')


@admin.register(models.Demanda)
class DemandaAdmin(admin.ModelAdmin):
    class Meta:
        js = (
            'static/js/jquery.mask.js',
            'js/jquery-3.5.1,js',
            'static/js/script.js',
        )

    list_display = ('anunciante', 'short_description', 'celular', 'telefone', 'get_country', 'is_closed')
    list_filter = ('status',)
    search_fields = ('anunciante', 'status',)
    ordering = ('anunciante', '-created_at')
    inlines = (EnderecoInline,)

    fieldsets = (
        (None, {'fields': ('anunciante', 'descricao', 'celular', 'telefone', 'status', 'created_at', 'updated_at',)}),
    )

    def is_closed(self, obj):
        true_icon = '<img src="/static/img/true.svg" alt="True">'
        false_icon = '<img src="/static/img/false.svg" alt="False">'

        print(obj.status)
        if obj.status == '0':
            return mark_safe('%s' % true_icon)
        else:
            return mark_safe('%s' % false_icon)

    is_closed.allow_tags = True
    is_closed.short_description = 'Status'

    def get_country(self, obj):
        endereco = models.Endereco.objects.get(demanda=obj)
        return endereco.pais

    get_country.short_description = 'País'
    get_country.admin_order_field = 'endereco__pais'

    readonly_fields = ('created_at', 'updated_at',)


# Custom admin name
admin.site.site_title = settings.APP_NAME
admin.site.site_header = settings.APP_NAME
admin.site.index_title = settings.APP_NAME
