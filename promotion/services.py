from datetime import date
from core.models import Articulo
from .models import Promotion

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
            valor = 0

            for item in items:
                articulo = articulos[item["articulo_id"]]
                if regla.articulo and articulo != regla.articulo:
                    continue
                if regla.linea and articulo.linea != regla.linea:
                    continue
                if regla.grupo and articulo.grupo != regla.grupo:
                    continue

                if regla.rule_type == "quantity":
                    valor += item["cantidad"]
                elif regla.rule_type == "amount":
                    valor += item["cantidad"] * item["precio_unitario"]

            # Evaluar escalas primero
            if regla.tiers.exists():
                for tier in regla.tiers.all():
                    if valor >= tier.min_value and (tier.max_value is None or valor <= tier.max_value):
                        promociones_aplicables.append({
                            "promotion": promo.name,
                            "description": promo.description,
                            "rewards": [{
                                "type": tier.reward_type,
                                "product_code": tier.product_code,
                                "quantity": tier.quantity,
                                "discount": tier.discount_percent
                            }]
                        })
                        break
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
                        if r.reward_type == "product":
                            recompensas_proporcionales.append({
                                "type": r.reward_type,
                                "product_code": r.product_code,
                                "quantity": r.quantity * veces if r.quantity else 0,
                                "discount": None
                            })
                        elif r.reward_type == "discount":
                            recompensas_proporcionales.append({
                                "type": r.reward_type,
                                "product_code": None,
                                "quantity": None,
                                "discount": float(r.discount_percent)  # descuento no se multiplica
                            })

                    promociones_aplicables.append({
                        "promotion": promo.name,
                        "description": promo.description,
                        "rewards": recompensas_proporcionales
                    })


    return promociones_aplicables
