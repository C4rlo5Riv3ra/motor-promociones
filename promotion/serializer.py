from rest_framework import serializers
from core.models import Empresa, Sucursal, CanalCliente, Articulo


class PedidoItemSerializer(serializers.Serializer):
    articulo_id = serializers.UUIDField()
    cantidad = serializers.IntegerField(min_value=1)
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_articulo_id(self, value):
        if not Articulo.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Artículo no encontrado.")
        return value


class PedidoSerializer(serializers.Serializer):
    empresa_id = serializers.UUIDField()
    sucursal_id = serializers.UUIDField()
    canal_id = serializers.CharField(max_length=3)
    items = PedidoItemSerializer(many=True)

    def validate_empresa_id(self, value):
        if not Empresa.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Empresa no encontrada.")
        return value

    def validate_sucursal_id(self, value):
        if not Sucursal.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Sucursal no encontrada.")
        return value

    def validate_canal_id(self, value):
        if not CanalCliente.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Canal de cliente no válido.")
        return value
