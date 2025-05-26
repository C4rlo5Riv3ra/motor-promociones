from rest_framework import serializers
from core.models import Empresa, Sucursal, CanalCliente, Articulo
from uuid import UUID

class ItemPedidoInputSerializer(serializers.Serializer):
    articulo_id = serializers.UUIDField()
    cantidad = serializers.IntegerField(min_value=1)
    precio_unitario = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_articulo_id(self, value):
        if not Articulo.objects.filter(pk=value).exists():
            raise serializers.ValidationError("El artículo no existe.")
        return value

class PedidoSerializer(serializers.Serializer):
    empresa_id = serializers.CharField()
    sucursal_id = serializers.UUIDField()
    canal_id = serializers.CharField(max_length=3)
    cliente_id = serializers.UUIDField(required=False, allow_null=True)
    items = ItemPedidoInputSerializer(many=True)

    def validate_empresa_id(self, value):
        if not Empresa.objects.filter(pk=value).exists():
            raise serializers.ValidationError("La empresa no existe.")
        return value

    def validate_sucursal_id(self, value):
        if not Sucursal.objects.filter(pk=value).exists():
            raise serializers.ValidationError("La sucursal no existe.")
        return value

    def validate_canal_id(self, value):
        if not CanalCliente.objects.filter(pk=value).exists():
            raise serializers.ValidationError("El canal no existe.")
        return value

    def validate(self, data):
        if not data.get("items"):
            raise serializers.ValidationError("Debe incluir al menos un item en el pedido.")
        return data
