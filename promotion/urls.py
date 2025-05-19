from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CondicionCreateView,
    CondicionDeleteView,
    CondicionUpdateView,
    evaluar_promocion_view,
    PromocionViewSet,
    CondicionPromocionViewSet,
    RangoCondicionViewSet,
    BonificacionViewSet,
    DescuentoViewSet,
    CondicionListView,
    RangoListView,
    BonificacionListView,
    DescuentoListView,

    DashboardView,
    PromocionListView,
    PromocionCreateView,
    PromocionUpdateView,
    PromocionDeleteView,

)


router = DefaultRouter()
router.register(r'promociones', PromocionViewSet)
router.register(r'condiciones', CondicionPromocionViewSet)
router.register(r'rangos', RangoCondicionViewSet)
router.register(r'bonificaciones', BonificacionViewSet)
router.register(r'descuentos', DescuentoViewSet)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),

    path('api/', include(router.urls)),

    path('evaluar-promocion/', evaluar_promocion_view, name='evaluar_pedido'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('promociones/', PromocionListView.as_view(), name='promocion_list'),
    path('promociones/nueva/', PromocionCreateView.as_view(), name='promocion_create'),
    path('promociones/<uuid:pk>/editar/', PromocionUpdateView.as_view(), name='promocion_update'),
    path('promocion/<uuid:pk>/eliminar/', PromocionDeleteView.as_view(), name='promocion_delete'),


  # CONDICIONES
   # Listar condiciones de una promoción
    path('condiciones/<uuid:promocion_id>/', CondicionListView.as_view(), name='condicion_list'),

    # Crear una nueva condición para esa promoción
    path('condiciones/<uuid:promocion_id>/nueva/', CondicionCreateView.as_view(), name='condicion_create'),

    # Editar y eliminar condiciones por su ID
    path('condiciones/<uuid:pk>/editar/', CondicionUpdateView.as_view(), name='condicion_update'),

    path('condiciones/<uuid:pk>/eliminar/', CondicionDeleteView.as_view(), name='condicion_delete'),





    path('rangos/', RangoListView.as_view(), name='rango_lista_general'),
    path('bonificaciones/', BonificacionListView.as_view(), name='bonificacion_lista_general'),
    path('descuentos/', DescuentoListView.as_view(), name='descuento_lista_general'),
   
]
