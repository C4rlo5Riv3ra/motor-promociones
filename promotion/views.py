from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Cliente, Articulo
from orders.models import Pedido, ItemPedido
from promotion.models import Promotion
from .serializer import PedidoSerializer
from .services import evaluate_promotions
from decimal import Decimal
import uuid

class EvaluarPromocionesView(APIView):
    def post(self, request):
        serializer = PedidoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        promociones = evaluate_promotions(data)

        # Obtener cliente (por cliente_id si se envió, si no por canal_id)
        cliente_id = data.get("cliente_id")
        if cliente_id:
            cliente = Cliente.objects.filter(cliente_id=cliente_id).first()
        else:
            canal_id = data.get("canal_id")
            cliente = Cliente.objects.filter(canal_id=canal_id).first()

        if not cliente:
            return Response(
                {"error": "No se encontró un cliente válido para el canal especificado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        subtotal = sum(Decimal(item["cantidad"]) * item["precio_unitario"] for item in data["items"])

        descuento_total = Decimal("0.00")
        for promo in promociones:
            # Verificamos que promo no sea None y tenga rewards
            if promo and "rewards" in promo:
                for beneficio in promo["rewards"]:
                    if beneficio and beneficio.get("tipo") == "descuento" and beneficio.get("porcentaje"):
                        porcentaje = Decimal(str(beneficio["porcentaje"]))
                        descuento_total += (porcentaje / Decimal("100")) * subtotal

        pedido = Pedido.objects.create(
            pedido_id=uuid.uuid4(),
            nro_pedido=Pedido.objects.count() + 1,
            importe=subtotal,
            monto_total=subtotal - descuento_total,
            descuento_aplicado=descuento_total,
            estado=1,
            cliente=cliente
        )

        # Crear ítems del pedido (compra)
        for item in data["items"]:
            articulo = Articulo.objects.get(pk=item["articulo_id"])
            ItemPedido.objects.create(
                item_id=uuid.uuid4(),
                pedido_id=pedido,
                articulo_id=articulo,
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
                total=Decimal(item["cantidad"]) * Decimal(item["precio_unitario"]),
                es_bonificacion=False,
                estado=1
            )

        # Asociar promociones y registrar bonificaciones
        for promo in promociones:
            if not promo:
                continue
            promo_obj = Promotion.objects.filter(name=promo.get("promotion")).first()
            if promo_obj:
                pedido.promociones_aplicadas.add(promo_obj)

            for beneficio in promo.get("rewards", []):
                if beneficio and beneficio.get("tipo") == "producto" and beneficio.get("codigo"):
                    articulo_bonificado = Articulo.objects.filter(codigo_articulo=beneficio["codigo"]).first()
                    if articulo_bonificado:
                        ItemPedido.objects.create(
                            item_id=uuid.uuid4(),
                            pedido_id=pedido,
                            articulo_id=articulo_bonificado,
                            cantidad=beneficio.get("cantidad", 1),
                            precio_unitario=Decimal("0.00"),
                            total=Decimal("0.00"),
                            es_bonificacion=True,
                            estado=1
                        )

        # Construir la respuesta asegurando que beneficios no contenga nulls
        promociones_response = []
        for p in promociones:
            if not p:
                continue
            beneficios_filtrados = [b for b in p.get("rewards", []) if b is not None and isinstance(b, dict)]
            promociones_response.append({
                "promocion": p.get("promotion"),
                "descripcion": p.get("description"),
                "beneficios": beneficios_filtrados
            })

        return Response({
            "mensaje": "El pedido fue registrado correctamente.",
            "id_pedido": str(pedido.pedido_id),
            "promociones_aplicadas": promociones_response
        }, status=status.HTTP_201_CREATED)