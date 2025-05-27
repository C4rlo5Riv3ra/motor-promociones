from datetime import date
from decimal import Decimal
from core.models import Articulo
from promotion.models import Promotion

def clean_reward(r):  # limpiar recompensa
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
    return None

def evaluate_promotions(pedido):
    hoy = date.today()
    promociones_aplicables = []

    empresa_id = pedido["empresa_id"]  
    items = pedido["items"]
    articulo_ids = [item["articulo_id"] for item in items]  # obtener ids de articulos
    articulos = Articulo.objects.in_bulk(articulo_ids)  # buscar articulos
    # filtrar promociones por fechas y canal
    promociones = Promotion.objects.filter(
        start_date__lte=hoy,
        end_date__gte=hoy,
        empresa_id=empresa_id,
        sucursal_id=pedido["sucursal_id"],
        canal_cliente_id=pedido["canal_id"]
    )

    # recorrer cada promoción
    for promo in promociones:
        rules = list(promo.rules.all())

        # --- COMBO ---
        if any(r.rule_type == "combo" for r in rules):  # si tiene combo
            combo_rules = [r for r in rules if r.rule_type == "combo"]  # filtrar combos
            required_ids = set(r.articulo_id for r in combo_rules)  # obtener ids de articulos necesarios
            ids_en_pedido = set( 
                articulos.get(item["articulo_id"]).articulo_id 
                for item in items if item["articulo_id"] in articulos
            )  # obtener ids de articulos en pedido

            if required_ids.issubset(ids_en_pedido):  # si todos los ids son en pedido
                recompensas_combo = []
                for r in promo.rewards.all():  # recorrer recompensas
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
            continue  # ya evaluado

        # --- CANTIDAD / MONTO + TIERS ---
        for regla in rules:  # recorrer cada regla
            valor = Decimal("0")
            for item in items:  # recorrer cada item
                articulo = articulos.get(item["articulo_id"])  # buscar articulo
                if not articulo:
                    continue
                if regla.articulo and articulo != regla.articulo:  # si regla tiene articulo y no es el mismo
                    continue
                if regla.linea and articulo.linea != regla.linea:  # si regla tiene linea y no es la misma
                    continue
                if regla.grupo and articulo.grupo != regla.grupo:  # si regla tiene grupo y no es el mismo
                    continue

                if regla.rule_type == "quantity":  # si es cantidad
                    valor += Decimal(item["cantidad"])  # sumar cantidad
                elif regla.rule_type == "amount":  # si es monto
                    valor += Decimal(item["cantidad"]) * Decimal(item["precio_unitario"])  # sumar cantidad x precio

            # --- Escalas (tiers) ---
            if regla.tiers.exists():  # si tienes tiers
                tiers_aplicables = [
                    tier for tier in regla.tiers.order_by("min_value")  # ordenar por min_value
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
            else:
                # --- Sin tiers: aplicar promoción estándar proporcional ---
                if regla.rule_type == "quantity" and regla.min_quantity and valor >= regla.min_quantity:
                    veces = int(valor // regla.min_quantity)  # calcular cantidad de veces
                elif regla.rule_type == "amount" and regla.min_amount and valor >= regla.min_amount:
                    veces = int(valor // regla.min_amount)  # calcular cantidad de veces
                else:
                    veces = 0  # si no se cumple ninguna condición, no aplicar

                if veces > 0:  # si aplicar
                    recompensas_proporcionales = []
                    for r in promo.rewards.all():  # recorrer recompensas
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
