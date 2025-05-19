from django.db import models
from promotion_engine.choices import ESTADO_ENTIDADES, TipoCondicion, TipoPromocion
from core.models import Articulo, CanalCliente
import uuid


class Promocion(models.Model):
    promocion_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    tipo_promocion = models.CharField(max_length=5, choices=TipoPromocion.choices)
    condicion_base = models.CharField(max_length=10, choices=TipoCondicion.choices)
    canal_cliente = models.ForeignKey(CanalCliente, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.IntegerField(choices=ESTADO_ENTIDADES.choices, default=ESTADO_ENTIDADES.ACTIVO)
    aplica_escalado = models.BooleanField(default=False)

    class Meta:
        db_table = "promociones.promocion"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return self.nombre

class CondicionPromocion(models.Model):
    condicion_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='condiciones')
    articulo = models.ForeignKey('core.Articulo', on_delete=models.CASCADE, null=True, blank=True)
    linea = models.ForeignKey('core.LineaArticulo', on_delete=models.CASCADE, null=True, blank=True)
    monto_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cantidad_minima = models.PositiveIntegerField(null=True, blank=True)
    rango_escalado = models.BooleanField(default=False)

    class Meta:
        db_table = 'promociones.condicion_promocion'

    def __str__(self):
        return f"{self.articulo} - {self.linea} - {self.monto_minimo} - {self.cantidad_minima}"

class RangoCondicion(models.Model):
    rango_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    condicion = models.ForeignKey(CondicionPromocion, on_delete=models.CASCADE, related_name='rangos')
    minimo = models.DecimalField(max_digits=12, decimal_places=2)  # puede ser monto o cantidad
    maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'promociones.rango_condicion'

    def __str__(self):
        return f"{self.minimo} - {self.maximo}"
    
class Bonificacion(models.Model):
    bonificacion_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='bonificaciones')
    condicion = models.ForeignKey(CondicionPromocion, on_delete=models.CASCADE, null=True, blank=True)
    rango = models.ForeignKey(RangoCondicion, on_delete=models.CASCADE, null=True, blank=True)
    articulo_bonificado = models.ForeignKey('core.Articulo', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    class Meta:
        db_table = 'promociones.bonificacion'

    def __str__(self):
        return f"{self.articulo_bonificado} - {self.cantidad}"

class Descuento(models.Model):
    descuento_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='descuentos')
    condicion = models.ForeignKey(CondicionPromocion, on_delete=models.CASCADE, null=True, blank=True)
    rango = models.ForeignKey(RangoCondicion, on_delete=models.CASCADE, null=True, blank=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'promociones.descuento'

    def __str__(self):
        return f"{self.porcentaje}"