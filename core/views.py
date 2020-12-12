from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core import models, serializers


class DemandaModelViewSet(viewsets.ModelViewSet):
    queryset = models.Demanda.objects.none()
    serializer_class = serializers.DemandaSerializerV1
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = models.Demanda.objects.none()
        # Se for Administrador pode ver tudo
        if self.request.user.groups.filter(name__in=('Administrador',)).exists():
            queryset = models.Demanda.objects.all()
        # Se for Anunciante só permite editar o seus registros
        if self.request.user.groups.filter(name__in=('Anunciante',)).exists():
            queryset = queryset.filter(anunciante_id=self.request.user.pk)
        return queryset

    # Endpoint para o Anunciante finalizar a demanda
    @action(methods=['post', ], detail=True, permission_classes=[IsAuthenticated])
    def finalizar_demanda(self, request, *args, **kwargs):
        demanda = self.object = self.get_object()
        if demanda.status == '0' and self.object.editor == request.user:
            demanda.status = '1'
            demanda.save()
