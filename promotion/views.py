from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Cliente, Articulo
from orders.models import Pedido, ItemPedido
from promotion.models import Promotion
from .serializer import PedidoSerializer
from .services import evaluate_promotions
from decimal import Decimal
from datetime import datetime
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
            promo_obj = Promotion.objects.filter(name=promo.get("promotion")).first()  # buscar promocion
            if promo_obj:
                pedido.promociones_aplicadas.add(promo_obj)  # agregar promocion a pedido

            for beneficio in promo.get("rewards", []):  # recorrer beneficios
                if beneficio and beneficio.get("tipo") == "producto" and beneficio.get("codigo"):  # si es producto y tiene codigo
                    articulo_bonificado = Articulo.objects.filter(codigo_articulo=beneficio["codigo"]).first()  # buscar articulo
                    if articulo_bonificado:  # si existe
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
    

class ListaPedidosView(APIView):
    def get(self, request):
        pedidos = Pedido.objects.select_related('cliente')\
            .prefetch_related('promociones_aplicadas', 'itemp_pedido__articulo_id')

        # Filtros por cliente, fechas y promoción
        cliente_id = request.GET.get("cliente_id")
        fecha_inicio = request.GET.get("fecha_inicio")
        fecha_fin = request.GET.get("fecha_fin")
        promocion_nombre = request.GET.get("promocion")  # puede ser nombre exacto o parte

        if cliente_id:
            pedidos = pedidos.filter(cliente_id=cliente_id)

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                pedidos = pedidos.filter(pedido_id__date__gte=fecha_inicio)
            except ValueError:
                return Response({"error": "Formato de fecha_inicio inválido. Use YYYY-MM-DD."}, status=400)

        if fecha_fin:
            try:
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                pedidos = pedidos.filter(pedido_id__date__lte=fecha_fin)
            except ValueError:
                return Response({"error": "Formato de fecha_fin inválido. Use YYYY-MM-DD."}, status=400)

        if promocion_nombre:
            pedidos = pedidos.filter(promociones_aplicadas__name__icontains=promocion_nombre).distinct()

        resultado = []
        for pedido in pedidos:
            articulos = []
            for item in pedido.itemp_pedido.all():
                articulos.append({
                    "codigo": item.articulo_id.codigo_articulo,
                    "descripcion": item.articulo_id.descripcion,
                    "cantidad": item.cantidad,
                    "precio_unitario": float(item.precio_unitario),
                    "total": float(item.total),
                    "es_bonificacion": item.es_bonificacion
                })

            promociones = [
                {
                    "nombre": promo.name,
                    "descripcion": promo.description
                }
                for promo in pedido.promociones_aplicadas.all()
            ]

            resultado.append({
                "id_pedido": str(pedido.pedido_id),
                "nro_pedido": pedido.nro_pedido,
                "cliente": pedido.cliente.nombres,
                "importe": float(pedido.importe),
                "descuento_aplicado": float(pedido.descuento_aplicado),
                "monto_total": float(pedido.monto_total),
                "promociones": promociones,
                "articulos": articulos
            })

        return Response(resultado, status=status.HTTP_200_OK)