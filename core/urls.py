from django.urls import path, include

from rest_framework import routers

from core import views

router = routers.SimpleRouter()
router.register(r'demanda', views.DemandaModelViewSet)


urlpatterns = [
    path('', include(router.urls))
]
