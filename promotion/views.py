import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import PedidoSerializer
from .services import evaluate_promotions
from orders.models import Pedido, ItemPedido
from core.models import Cliente, Articulo
from promotion.models import Promotion

from decimal import Decimal

class EvaluarPromocionesView(APIView):
    def post(self, request):
        serializer = PedidoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        promociones = evaluate_promotions(data)

        # ⚠️ Temporal: obtener un cliente (en producción usar auth o incluir en payload)
        cliente = Cliente.objects.first()
        if not cliente:
            return Response({"error": "No hay cliente en la base de datos."}, status=status.HTTP_400_BAD_REQUEST)

        # Subtotal sin descuentos
        subtotal = sum(Decimal(item["cantidad"]) * item["precio_unitario"]for item in data["items"])


        # Calcular descuento total (porcentaje aplicado)
        descuento_total = 0
        for promo in promociones:
            for reward in promo["rewards"]:
                if reward["tipo"] == "discount" and reward["discount"]:
                    porcentaje = Decimal(str(reward["discount"]))
                    descuento_total += (porcentaje / Decimal('100')) * subtotal

        # Crear pedido
        pedido = Pedido.objects.create(
            pedido_id=uuid.uuid4(),
            nro_pedido=Pedido.objects.count() + 1,
            importe=subtotal,
            monto_total=subtotal - descuento_total,
            descuento_aplicado=descuento_total,
            estado=1,
            cliente=cliente
        )

        # Crear ítems del pedido
        for item in data["items"]:
            articulo = Articulo.objects.get(pk=item["articulo_id"])
            ItemPedido.objects.create(
                item_id=uuid.uuid4(),
                pedido_id=pedido,
                articulo_id=articulo,
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
                total=item["cantidad"] * item["precio_unitario"],
                es_bonificacion=False,
                estado=1
            )

        # Asociar promociones y registrar productos bonificados
        for promo in promociones:
            try:
                promo_obj = Promotion.objects.get(name=promo["promotion"])
                pedido.promociones_aplicadas.add(promo_obj)
            except Promotion.DoesNotExist:
                continue

            for reward in promo["rewards"]:
                if reward["tipo"] == "product" and reward["product_code"]:
                    try:
                        articulo_bonificado = Articulo.objects.get(codigo_articulo=reward["product_code"])
                        ItemPedido.objects.create(
                            item_id=uuid.uuid4(),
                            pedido_id=pedido,
                            articulo_id=articulo_bonificado,
                            cantidad=reward["quantity"],
                            precio_unitario=0.00,
                            total=0.00,
                            es_bonificacion=True,
                            estado=1
                        )
                    except Articulo.DoesNotExist:
                        continue

        return Response({
            "mensaje": "El pedido fue registrado correctamente.",
            "id_pedido": str(pedido.pedido_id),
            "promociones_aplicadas": [
                {
                    "promocion": p["promotion"],
                    "descripcion": p["description"],
                    "beneficios": p["rewards"]
                } for p in promociones
            ]
        }, status=status.HTTP_201_CREATED)
