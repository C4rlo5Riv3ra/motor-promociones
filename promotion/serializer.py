from rest_framework import serializers
from core.models import *
from promotion.models import *

# ------------------------- Serializers Básicos -------------------------
class ArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articulo
        fields = ['articulo_id', 'codigo_articulo', 'descripcion']

class CanalClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanalCliente
        fields = ['canal_id', 'nombre_canal']

# ------------------------- Serializers Anidados -------------------------
class RecompensaPromocionSerializer(serializers.ModelSerializer):
    articulo = ArticuloSerializer()

    class Meta:
        model = RecompensaPromocion
        fields = ['id', 'articulo', 'cantidad', 'porcentaje']

class ReglaPromocionSerializer(serializers.ModelSerializer):
    beneficios = RecompensaPromocionSerializer(many=True, read_only=True)
    articulo = ArticuloSerializer()

    class Meta:
        model = ReglaPromocion
        fields = [
            'id', 'articulo', 'grupo', 'linea', 
            'minimo_monto', 'minimo_cantidad', 'beneficios'
        ]

class ReglaEscalaSerializer(serializers.ModelSerializer):
    beneficios = RecompensaPromocionSerializer(many=True, read_only=True)

    class Meta:
        model = ReglaEscala
        fields = [
            'id', 'rango_inicio', 'rango_fin', 
            'descuento', 'beneficios'
        ]

# ------------------------- Serializer Principal de Promoción -------------------------
class PromocionSerializer(serializers.ModelSerializer):
    empresa = serializers.StringRelatedField()
    sucursal = serializers.StringRelatedField()
    canal = CanalClienteSerializer()
    reglas = ReglaPromocionSerializer(many=True, read_only=True, source='reglas')
    escalas = ReglaEscalaSerializer(many=True, read_only=True, source='escalas')

    class Meta:
        model = Promocion
        fields = [
            'id', 'nombre', 'tipo_promocion', 'fecha_inicio', 
            'fecha_fin', 'empresa', 'sucursal', 'canal', 
            'reglas', 'escalas'
        ]

# ------------------------- Serializers para Reglas Específicas -------------------------
class RequisitoCompraConjuntaSerializer(serializers.ModelSerializer):
    articulo = ArticuloSerializer()

    class Meta:
        model = RequisitoCompraConjunta
        fields = ['id', 'articulo', 'cantidad_minima']

class ReglaCompraConjuntaSerializer(serializers.ModelSerializer):
    requisitos = RequisitoCompraConjuntaSerializer(many=True, read_only=True)

    class Meta:
        model = ReglaCompraConjunta
        fields = ['id', 'promocion', 'descuento', 'requisitos']

class ArticuloAcumulableSerializer(serializers.ModelSerializer):
    articulo = ArticuloSerializer()

    class Meta:
        model = ArticuloAcumulable
        fields = ['id', 'articulo']

class RecompensaReglaAcumuladaSerializer(serializers.ModelSerializer):
    articulo = ArticuloSerializer()

    class Meta:
        model = RecompensaReglaAcumulada
        fields = ['id', 'articulo', 'cantidad', 'porcentaje']

class ReglaProductosAcumuladosSerializer(serializers.ModelSerializer):
    articulos = ArticuloAcumulableSerializer(many=True, read_only=True)
    beneficios = RecompensaReglaAcumuladaSerializer(many=True, read_only=True)

    class Meta:
        model = ReglaProductosAcumulados
        fields = [
            'id', 'grupo', 'linea', 'minimo_cantidad_total', 
            'articulos', 'beneficios'
        ]

# En promotions/api/serializers.py
class PedidoEvaluacionSerializer(serializers.Serializer):
    cliente_id = serializers.UUIDField()
    canal_cliente = serializers.CharField()
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            allow_empty=False
        )
    )
    monto_total = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        # Aquí puedes agregar validaciones adicionales
        # Ej: Verificar que el cliente exista
        return data