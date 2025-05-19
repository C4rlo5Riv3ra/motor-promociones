from rest_framework import serializers
from .models import Pedido, ItemPedido
from core.models import Cliente

class ItemPedidoSerializer(serializers.ModelSerializer):
    articulo_nombre = serializers.CharField(source='articulo_id.descripcion', read_only=True)
    class Meta:
        model = ItemPedido
        fields = ['item_id', 'articulo_nombre', 'cantidad', 'precio_unitario', 'total']

class PedidoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombres', read_only=True)
    items = serializers.SerializerMethodField()
    promociones = serializers.StringRelatedField(many=True, source='promociones_aplicadas')

    class Meta:
        model = Pedido
        fields = ['pedido_id', 'nro_pedido', 'cliente_nombre', 'importe', 'descuento_aplicado', 'monto_total', 'promociones', 'items']

    def get_items(self, obj):
        items = obj.itemps_pedido.all()
        return ItemPedidoSerializer(items, many=True).data
