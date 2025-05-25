from datetime import date
from decimal import Decimal
from core.models import Articulo
from .models import Promotion

def clean_reward(r):
    if r["type"] == "product":
        try:
            articulo = Articulo.objects.get(codigo_articulo=r["product_code"])
            descripcion = articulo.descripcion
        except Articulo.DoesNotExist:
            descripcion = None

        return {
            "tipo": "producto",
            "codigo": r["product_code"],
            "descripcion": descripcion,
            "cantidad": r["quantity"]
        }
    elif r["type"] == "discount":
        return {
            "tipo": "descuento",
            "porcentaje": r["discount"]
        }


def evaluate_promotions(pedido):
    hoy = date.today()
    promociones_aplicables = []

    items = pedido["items"]
    articulo_ids = [item["articulo_id"] for item in items]
    articulos = Articulo.objects.in_bulk(articulo_ids)

    promociones = Promotion.objects.filter(
        start_date__lte=hoy,
        end_date__gte=hoy,
        empresa_id=pedido["empresa_id"],
        sucursal_id=pedido["sucursal_id"],
        canal_cliente_id=pedido["canal_id"]
    )

    for promo in promociones:
        for regla in promo.rules.all():
            valor = Decimal("0")

            for item in items:
                articulo = articulos[item["articulo_id"]]

                if regla.articulo and articulo.articulo_id != regla.articulo.articulo_id:
                    continue
                if regla.linea and articulo.linea_id != regla.linea.linea_id:
                    continue
                if regla.grupo and articulo.grupo_id != regla.grupo.grupo_id:
                    continue

                if regla.rule_type == "quantity":
                    valor += item["cantidad"]
                elif regla.rule_type == "amount":
                    valor += Decimal(item["cantidad"]) * item["precio_unitario"]

            # Evaluar escalas (tiers)
            if regla.tiers.exists():
                tiers_aplicables = [
                    tier for tier in regla.tiers.order_by("min_value")
                    if valor >= tier.min_value and (tier.max_value is None or valor <= tier.max_value)
                ]

                if tiers_aplicables:
                    promociones_aplicables.append({
                        "promotion": promo.name,
                        "description": promo.description,
                        "rewards": [
                            clean_reward({
                                "type": tier.reward_type,
                                "product_code": tier.product_code,
                                "quantity": tier.quantity,
                                "discount": float(tier.discount_percent) if tier.reward_type == "discount" else None
                            }) for tier in tiers_aplicables
                        ]
                    })
            else:
                if regla.rule_type == "quantity" and regla.min_quantity and valor >= regla.min_quantity:
                    veces = int(valor // regla.min_quantity)
                elif regla.rule_type == "amount" and regla.min_amount and valor >= regla.min_amount:
                    veces = int(valor // regla.min_amount)
                else:
                    veces = 0

                if veces > 0:
                    recompensas = promo.rewards.all()
                    recompensas_proporcionales = []

                    for r in recompensas:
                        recompensa = {
                            "type": r.reward_type,
                            "product_code": r.product_code if r.reward_type == "product" else None,
                            "quantity": r.quantity * veces if r.reward_type == "product" and r.quantity else None,
                            "discount": float(r.discount_percent) if r.reward_type == "discount" else None
                        }
                        recompensas_proporcionales.append(clean_reward(recompensa))

                    promociones_aplicables.append({
                        "promotion": promo.name,
                        "description": promo.description,
                        "rewards": recompensas_proporcionales
                    })

    return promociones_aplicables
