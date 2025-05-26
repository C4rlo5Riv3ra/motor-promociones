from django.db import models
from core.models import *

class Promotion(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    canal_cliente = models.ForeignKey(CanalCliente, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class PromotionRule(models.Model):
    RULE_TYPE_CHOICES = [
        ('quantity', 'Cantidad'),
        ('amount', 'Monto'),
        ('combo', 'Combo Productos'),
    ]
    promotion = models.ForeignKey(Promotion, related_name='rules', on_delete=models.CASCADE)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    articulo = models.ForeignKey(Articulo, null=True, blank=True, on_delete=models.CASCADE)
    min_quantity = models.PositiveIntegerField(blank=True, null=True)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    linea = models.ForeignKey(LineaArticulo, null=True, blank=True, on_delete=models.CASCADE)
    grupo = models.ForeignKey(GrupoArticulo, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Regla de {self.promotion.name}"


class PromotionReward(models.Model):
    REWARD_TYPE_CHOICES = [
        ('product', 'Producto Bonificado'),
        ('discount', 'Descuento %'),
    ]
    promotion = models.ForeignKey(Promotion, related_name='rewards', on_delete=models.CASCADE)
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES)
    product_code = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Beneficio de {self.promotion.name}"


class PromotionRuleTier(models.Model):
    rule = models.ForeignKey('PromotionRule', related_name='tiers', on_delete=models.CASCADE)
    min_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reward_type = models.CharField(max_length=20, choices=PromotionReward.REWARD_TYPE_CHOICES)
    product_code = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Escala de {self.rule.promotion.name} ({self.min_value} - {self.max_value or '∞'})"
