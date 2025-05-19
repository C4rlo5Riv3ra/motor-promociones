from rest_framework import serializers
from .models import Promocion, CondicionPromocion, RangoCondicion, Bonificacion, Descuento
from core.models import Articulo

class CondicionPromocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CondicionPromocion
        fields = '__all__'

class RangoCondicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RangoCondicion
        fields = '__all__'

class BonificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonificacion
        fields = '__all__'

class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = '__all__'

class PromocionSerializer(serializers.ModelSerializer):
    condiciones = CondicionPromocionSerializer(many=True, read_only=True)
    bonificaciones = BonificacionSerializer(many=True, read_only=True)
    descuentos = DescuentoSerializer(many=True, read_only=True)

    class Meta:
        model = Promocion
        fields = '__all__'
