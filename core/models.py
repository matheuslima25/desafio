import uuid

from django.contrib.auth.models import Group, AbstractUser
from django.db import models
from django.db.models import QuerySet, ProtectedError
from django.db.models import signals
from django.dispatch import receiver
from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext as _

from core import choices


class BaseModelQuerySet(QuerySet):

    def delete(self):
        [x.delete() for x in self]

    def hard_delete(self):
        [x.hard_delete() for x in self]

    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)


class BaseModelManager(models.Manager):
    use_for_related_fields = True

    def __init__(self, *args, **kwargs):
        self.active_only = kwargs.pop('active_only', True)
        super(BaseModelManager, self).__init__(*args, **kwargs)

    def all_objects(self):
        return BaseModelQuerySet(self.model)

    def get_queryset(self):
        if self.active_only:
            return BaseModelQuerySet(self.model).filter(is_active=True)
        return BaseModelQuerySet(self.model)

    def hard_delete(self):
        self.get_queryset().hard_delete()


class BaseModel(models.Model):
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)
    is_active = models.BooleanField(
        editable=False, default=True, verbose_name='registro ativo'
    )

    objects = BaseModelManager()
    all_objects = BaseModelManager(active_only=False)

    def _on_delete(self):
        for relation in self._meta._relation_tree:
            on_delete = getattr(relation.remote_field, 'on_delete')

            if on_delete in [None, models.DO_NOTHING]:
                continue

            filter = {relation.name: self}
            related_queryset = relation.model.objects.filter(**filter)

            if on_delete == models.CASCADE:
                relation.model.objects.filter(**filter).delete()
            elif on_delete == models.SET_NULL:
                for r in related_queryset.all():
                    related_queryset.update(**{relation.name: None})
            elif on_delete == models.PROTECT:
                if related_queryset.count() > 0:
                    raise ProtectedError('Cannot remove this instances',
                                         related_queryset.all())
            else:
                raise NotImplementedError()

    def delete(self):
        self.is_active = False
        self.save()
        self._on_delete()

    def hard_delete(self):
        super(BaseModel, self).delete()

    class Meta:
        abstract = True


class Perfil(Group):
    class Meta:
        proxy = True
        verbose_name = _('Perfil')
        verbose_name_plural = _('Perfis')


class User(AbstractUser, BaseModel):
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['is_superuser', 'username', 'is_active']

    name = models.CharField(_('Nome'), max_length=150)
    groups = models.ManyToManyField(
        Perfil, verbose_name=_(u'Perfis'), blank=True,
        help_text='Os perfis que este usuário pertence.'
                  + ' Um usuário terá todas as permissões concedidas a'
                  + ' cada um dos seus perfis.', related_name="user_set",
        related_query_name="user"
    )
    is_staff = models.BooleanField(
        _(u'Membro'), default=True, help_text=_(
            _(u'Indica que usuário consegue acessar este site.')
        ),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return u'%s' % self.username


@receiver(signals.post_save, sender=User)
def user_post_save_signals(sender, instance, created, raw, using, *args, **kwargs):
    if created:
        if instance.is_superuser:
            group = Perfil.objects.get(name='Administrador')
            instance.groups.add(group.pk)
        else:
            group = Perfil.objects.get(name='Anunciante')
            instance.groups.add(group.pk)


class Demanda(BaseModel):
    class Meta:
        verbose_name = _(u'Demanda de Preço')
        verbose_name_plural = _(u'Demandas de Preço')

    anunciante = models.ForeignKey(User, verbose_name=_(u'Anunciante'), on_delete=models.CASCADE)
    descricao = models.CharField(_(u'Descrição'), max_length=150)
    status = models.CharField(_(u'Status de Finalização'), max_length=120, choices=choices.COMPLETION_CHOICES,
                              default='0')

    celular = models.CharField(_(u'Celular'), max_length=150, null=True)
    telefone = models.CharField(_(u'Telefone'), max_length=150, null=True, blank=True)

    @property
    def short_description(self):
        return truncatechars(self.descricao, 24)

    def __str__(self):
        return u'%s' % self.anunciante


class Endereco(BaseModel):
    class Meta:
        verbose_name = _(u'Endereço de Entrega')
        verbose_name_plural = _(u'Endereços de Entrega')

    demanda = models.ForeignKey(Demanda, on_delete=models.CASCADE)
    cep = models.CharField(_(u'CEP'), max_length=16, blank=True, null=True)
    pais = models.CharField(_(u'País'), max_length=20, blank=True, null=True, default='Brasil')
    estado = models.CharField(_(u'Estado'), max_length=120, blank=True, null=True, choices=choices.STATE_CHOICES)
    cidade = models.CharField(_(u'Cidade'), max_length=120, blank=True, null=True)
    rua = models.CharField(_(u'Rua'), max_length=255, blank=True, null=True)
    numero = models.CharField(_(u'Número'), max_length=10, blank=True, null=True)
    bairro = models.CharField(_(u'Bairro'), max_length=120, blank=True, null=True)
    complemento = models.CharField(_(u'Complemento'), max_length=255, blank=True, null=True)

    def cleaned_addr_cep(self):
        def _only_numbers(value):
            value = value or ''
            return ''.join(val for val in value if val.isdigit())

        return _only_numbers(self.cep)

    def __str__(self):
        return u'%s' % self.id
