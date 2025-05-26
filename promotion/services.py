from datetime import date
from decimal import Decimal
from core.models import Articulo
from promotion.models import Promotion

def clean_reward(r):
    # Normalizamos tipo para evitar confusiones
    tipo = r.get("tipo")
    if tipo in ["producto", "product"]:
        try:
            articulo = Articulo.objects.get(codigo_articulo=r.get("codigo"))
            return {
                "tipo": "producto",
                "codigo": r.get("codigo"),
                "descripcion": articulo.descripcion,
                "presentacion": articulo.unidad_bonificacion or articulo.unidad_reparto,
                "cantidad": r.get("cantidad") or 0
            }
        except Articulo.DoesNotExist:
            return {
                "tipo": "producto",
                "codigo": r.get("codigo"),
                "descripcion": None,
                "presentacion": None,
                "cantidad": r.get("cantidad") or 0
            }
    elif tipo in ["descuento", "discount"]:
        return {
            "tipo": "descuento",
            "porcentaje": r.get("porcentaje") or 0.0
        }
    else:
        # Si el tipo no es reconocido, devolver algo neutro o None para evitar errores
        return None

def evaluate_promotions(pedido):
    hoy = date.today()
    promociones_aplicables = []

    empresa_id = pedido["empresa_id"]
    items = pedido["items"]
    articulo_ids = [item["articulo_id"] for item in items]
    articulos = Articulo.objects.in_bulk(articulo_ids)

    promociones = Promotion.objects.filter(
        start_date__lte=hoy,
        end_date__gte=hoy,
        empresa_id=empresa_id,
        sucursal_id=pedido["sucursal_id"],
        canal_cliente_id=pedido["canal_id"]
    )

    for promo in promociones:
        for regla in promo.rules.all():
            valor = Decimal("0")

            for item in items:
                articulo = articulos.get(item["articulo_id"])
                if not articulo:
                    continue
                if regla.articulo and articulo != regla.articulo:
                    continue
                if regla.linea and articulo.linea != regla.linea:
                    continue
                if regla.grupo and articulo.grupo != regla.grupo:
                    continue

                if regla.rule_type == "quantity":
                    valor += Decimal(item["cantidad"])
                elif regla.rule_type == "amount":
                    valor += Decimal(item["cantidad"]) * Decimal(item["precio_unitario"])

            if regla.tiers.exists():
                tiers_aplicables = [
                    tier for tier in regla.tiers.order_by("min_value")
                    if valor >= tier.min_value and (tier.max_value is None or valor <= tier.max_value)
                ]

                if tiers_aplicables:
                    rewards_cleaned = []
                    for tier in tiers_aplicables:
                        reward_dict = {
                            "tipo": "producto" if tier.reward_type == "product" else "descuento",
                            "codigo": tier.product_code,
                            "cantidad": tier.quantity,
                            "porcentaje": float(tier.discount_percent) if tier.reward_type == "discount" else None
                        }
                        cleaned = clean_reward(reward_dict)
                        if cleaned:
                            rewards_cleaned.append(cleaned)

                    promociones_aplicables.append({
                        "promotion": promo.name,
                        "description": promo.description,
                        "rewards": rewards_cleaned
                    })

                elif regla.rule_type == "combo":
                    combo_rules = promo.rules.filter(rule_type="combo")
                    required_articulos_ids = set(combo_rules.values_list("articulo_id", flat=True))
                    articulos_en_pedido_ids = set(articulos.get(item["articulo_id"]).articulo_id for item in items if item["articulo_id"] in articulos)

                    if required_articulos_ids.issubset(articulos_en_pedido_ids):
                        recompensas = promo.rewards.all()
                        recompensas_combo = []

                        for r in recompensas:
                            recompensa = {
                                "tipo": "producto" if r.reward_type == "product" else "descuento",
                                "codigo": r.product_code if r.reward_type == "product" else None,
                                "cantidad": r.quantity if r.reward_type == "product" else None,
                                "porcentaje": float(r.discount_percent) if r.reward_type == "discount" else None
                            }
                            cleaned = clean_reward(recompensa)
                            if cleaned:
                                recompensas_combo.append(cleaned)

                        promociones_aplicables.append({
                            "promotion": promo.name,
                            "description": promo.description,
                            "rewards": recompensas_combo
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
                            "tipo": "producto" if r.reward_type == "product" else "descuento",
                            "codigo": r.product_code if r.reward_type == "product" else None,
                            "cantidad": r.quantity * veces if r.reward_type == "product" and r.quantity else 0,
                            "porcentaje": float(r.discount_percent) if r.reward_type == "discount" else None
                        }
                        cleaned = clean_reward(recompensa)
                        if cleaned:
                            recompensas_proporcionales.append(cleaned)

                    promociones_aplicables.append({
                        "promotion": promo.name,
                        "description": promo.description,
                        "rewards": recompensas_proporcionales
                    })

    return promociones_aplicables