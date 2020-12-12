from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers

from core import models, serializers


class DemandaModelViewSet(viewsets.ModelViewSet):
    queryset = models.Demanda.objects.none()
    serializer_class = serializers.DemandaSerializerV1
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        if serializer.is_valid():
            obj = serializer.save()
        endereco_data = {
            'demanda': obj.id,
            'cep': self.request.data.get('endereco', None).get('cep', None),
            'pais': self.request.data.get('endereco', None).get('pais', None),
            'estado': self.request.data.get('endereco', None).get('estado', None),
            'cidade': self.request.data.get('endereco', None).get('cidade', None),
            'numero': self.request.data.get('endereco', None).get('numero', None),
            'bairro': self.request.data.get('endereco', None).get('bairro', None),
            'complemento': self.request.data.get('endereco', None).get('complemento', None),
        }
        endereco = serializers.EnderecoSerializerV1(data=endereco_data)
        if endereco.is_valid():
            endereco.save()
        serializer.save()

    def perform_update(self, serializer):
        if serializer.is_valid():
            obj = serializer.save()
        models.Endereco.objects.update_or_create(
            demanda_id=obj.id,
            cep=self.request.data.get('endereco', None).get('cep', None),
            pais=self.request.data.get('endereco', None).get('pais', None),
            estado=self.request.data.get('endereco', None).get('estado', None),
            cidade=self.request.data.get('endereco', None).get('cidade', None),
            numero=self.request.data.get('endereco', None).get('numero', None),
            bairro=self.request.data.get('endereco', None).get('bairro', None),
            complemento=self.request.data.get('endereco', None).get('complemento', None)
        )
        serializer.save()

    def get_queryset(self):
        queryset = models.Demanda.objects.none()
        # Se for Administrador pode ver tudo
        if self.request.user.groups.filter(name__in=('Administrador',)).exists():
            queryset = models.Demanda.objects.all()
        # Se for Anunciante só permite editar o seus registros
        if self.request.user.groups.filter(name__in=('Anunciante',)).exists():
            queryset = models.Demanda.objects.filter(anunciante_id=self.request.user.pk)
        return queryset

    # Endpoint para o Anunciante finalizar a demanda
    @action(methods=['post', ], detail=True, permission_classes=[IsAuthenticated])
    def finalizar_demanda(self, request, *args, **kwargs):
        demanda = self.object = self.get_object()
        if demanda.status == '0' and self.object.anunciante == request.user:
            demanda.status = '1'
            demanda.save()
            return Response(status=status.HTTP_200_OK, data='Demanda finalizada com sucesso.')
        raise drf_serializers.ValidationError('Demanda não encontrada ou já finalizada.')

    def perform_destroy(self, instance):
        try:
            models.Demanda.objects.get(id=instance.pk).delete()
        except Http404:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_200_OK)

