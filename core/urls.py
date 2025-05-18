from django.urls import path 
from . import views

urlpatterns = [ 
    # URLs para Artículos 
    path('articulos/', views.articulos_list, name='articulos_list'), 
    path('articulos/nuevo/', views.articulo_create, name='articulo_create'), 
]