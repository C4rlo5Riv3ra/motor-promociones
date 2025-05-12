from django.db import models
from catalogs.models import Articulo, GrupoArticulo, Empresa, Sucursal, CanalCliente
from promotion_engine.choices import TipoCondicion, TipoAccion
import uuid

# Create your models here.
class Promocion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Alcance
    empresas = models.ManyToManyField(Empresa)
    sucursales = models.ManyToManyField(Sucursal)
    canales = models.ManyToManyField(CanalCliente)
    
    # Condiciones
    tipo_condicion = models.IntegerField(choices=TipoCondicion, default=TipoCondicion.VOLUMEN)
    articulos_aplicables = models.ManyToManyField(Articulo, blank=True)
    grupos_aplicables = models.ManyToManyField(GrupoArticulo, blank=True)
    valor_minimo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Acciones
    tipo_accion = models.IntegerField(choices=TipoAccion, default=TipoAccion.DESCUENTO)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = "promocion"
        ordering = ['id']

class RangoPromocion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='rangos')
    min = models.DecimalField(max_digits=10, decimal_places=2)
    max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Rango {self.min} - {self.max} para {self.promocion.nombre}"
    
    class Meta:
        db_table = "rango_promocion"
        ordering = ['id']

class BonificacionProducto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='bonificaciones')
    producto = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"Bonificación de {self.cantidad} x {self.producto.descripcion} para {self.promocion.nombre}"

    class Meta:
        db_table = "bonificacion_producto"
        ordering = ['id']

class ProductoRequerido(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='productos_requeridos')
    producto = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad_minima = models.PositiveIntegerField()

    def __str__(self):
        return f"Producto requerido: {self.producto.descripcion} para {self.promocion.nombre}"

    class Meta:
        db_table = "producto_requerido"
        ordering = ['id']