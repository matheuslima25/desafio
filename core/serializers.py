from rest_framework import serializers
from rest_framework.status import HTTP_400_BAD_REQUEST

from core import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        exclude = (
            'is_superuser', 'is_staff', 'user_permissions', 'groups', 'date_joined', 'status', 'is_active',
            'created_at',
            'updated_at',)
        read_only_fields = ('last_login', 'date_joined', 'is_active', 'profile',)
        extra_kwargs = {'password': {'write_only': True}}

    profile = serializers.SerializerMethodField()

    def get_profile(self, obj):
        if obj and obj.groups.all():
            return obj.groups.values_list('name', flat=True)

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        if self.validated_data.get('password'):
            instance.set_password(self.validated_data.get('password'))
        return instance


class EnderecoSerializerV1(serializers.ModelSerializer):
    class Meta:
        error_status_codes = {
            HTTP_400_BAD_REQUEST: 'Bad Request'
        }
        model = models.Endereco
        fields = '__all__'


class DemandaSerializerV1(serializers.ModelSerializer):
    endereco = serializers.SerializerMethodField()

    class Meta:
        error_status_codes = {
            HTTP_400_BAD_REQUEST: 'Bad Request'
        }
        model = models.Demanda
        fields = ['anunciante', 'descricao', 'celular', 'telefone', 'status', 'endereco']

    def get_endereco(self, obj):
        return [EnderecoSerializerV1(s).data for s in obj.endereco_set.all()]
