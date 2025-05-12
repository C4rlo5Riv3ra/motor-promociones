from django.db import models
from catalogs.models import *
from promotion_engine.choices import EstadoEntidades, EstadoOrden
import uuid

# Create your models here.

# --- Pedidos ---

class Pedido(models.Model):
    pedido_id = models.UUIDField(primary_key=True)
    nro_pedido = models.IntegerField(null=False)
    cliente_id = models.ForeignKey(Cliente, on_delete=models.RESTRICT, null=False, related_name='cliente_pedido', db_column='cliente_id')
    importe = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)

    def __str__(self):
        return f"Pedido #{self.nro_pedido}"

    class Meta:
        db_table = 'pedido'
        ordering = ['pedido_id']

class ItemPedido(models.Model):
    item_id = models.UUIDField(primary_key=True)
    pedido_id = models.ForeignKey(Pedido, on_delete=models.RESTRICT, null=False, related_name='itemp_pedido', db_column='pedido_id')
    articulo_id = models.ForeignKey(Articulo, on_delete=models.RESTRICT, null=False, related_name='itemp_articulo', db_column='articulo_id')
    cantidad = models.IntegerField(null=False)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    total = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)

    class Meta:
        db_table = 'item_pedido'
        ordering = ['item_id']

class OrdenCompraCliente(models.Model):
    pedido_id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    nro_pedido = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    fecha_pedido = models.DateField(auto_now_add=True, null=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT,null=False)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.RESTRICT,null=False)
    importe = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.IntegerField(choices=EstadoOrden,default=EstadoOrden.PENDIENTE)
    notas = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.RESTRICT,null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=False)

    def actualizar_total(self):
        """Actualiza el total de la orden basado en los items"""
        total = sum(item.total_item for item in self.items_orden_compra.all())
        self.importe = total
        self.save()

    def __str__(self):
        return f"Orden #{self.nro_pedido} - {self.cliente}"

    class Meta:
        db_table = "ordenes_compra_cliente"
        ordering = ["-fecha_creacion"]

class ItemOrdenCompraCliente(models.Model):
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = models.ForeignKey(OrdenCompraCliente, on_delete=models.CASCADE, null=False, related_name='items_orden_compra')
    nro_item = models.PositiveIntegerField(default=1, null=False)
    articulo = models.ForeignKey(Articulo, on_delete=models.RESTRICT, null=False, related_name='articulo_item_orden_compra')
    cantidad = models.PositiveIntegerField(null=False, default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
    total_item = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)
    creado_por = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=False)

    def save(self, *args, **kwargs):
        # Si no se ha establecido el precio unitario, tomarlo del artículo
        if self.precio_unitario == 0:
            try:
                lista_precio = self.articulo.listaprecio
                self.precio_unitario = lista_precio.precio_1
            except Exception:
                pass  # Podrías registrar esto para auditoría

        # Calcular el total del ítem
        self.total_item = self.cantidad * self.precio_unitario

        super().save(*args, **kwargs)

        # Actualizar el total de la orden
        self.pedido.actualizar_total()

    def __str__(self):
        return f"{self.cantidad} x {self.articulo.descripcion}"

    class Meta:
        db_table = "items_ordenes_compra_cliente"
    
