from django.db import models
from core.models import TimeStampedModel ,Cliente, Articulo
from promotion.models import Promotion
from promotion_engine.choices import ESTADO_ENTIDADES

# Create your models here.

class Pedido(TimeStampedModel):
    pedido_id = models.UUIDField(primary_key=True)
    nro_pedido = models.IntegerField(null=False)
    importe = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    estado = models.IntegerField(choices=ESTADO_ENTIDADES.choices, default=ESTADO_ENTIDADES.ACTIVO)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    promociones_aplicadas = models.ManyToManyField(Promotion)

    def __str__(self):
        return f"Pedido #{self.nro_pedido}"

    class Meta:
        db_table = 'promociones.pedido'
        ordering = ['pedido_id']

class ItemPedido(TimeStampedModel):
    item_id = models.UUIDField(primary_key=True)
    pedido_id = models.ForeignKey(Pedido, on_delete=models.RESTRICT, null=False, related_name='itemp_pedido', db_column='pedido_id')
    articulo_id = models.ForeignKey(Articulo, on_delete=models.RESTRICT, null=False, related_name='itemp_articulo', db_column='articulo_id')
    cantidad = models.IntegerField(null=False)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    total = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    es_bonificacion = models.BooleanField(default=False)
    estado = models.IntegerField(choices=ESTADO_ENTIDADES.choices, default=ESTADO_ENTIDADES.ACTIVO)

    class Meta:
        db_table = 'promociones.item_pedido'
        ordering = ['item_id']

