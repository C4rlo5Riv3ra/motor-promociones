from django.db import models
from core.models import TimeStampedModel ,Articulo, GrupoArticulo, LineaArticulo, Empresa, Sucursal, CanalCliente
from promotion_engine.choices import TIPO_PROMOCION, TIPO_DESCUENTO
import uuid
# Create your models here.

class Promocion(TimeStampedModel):
    # ... (campos existentes, incluyendo ForeignKey a Empresa, Sucursal, CanalCliente)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    tipo_promocion = models.CharField(max_length=15, choices=TIPO_PROMOCION)
    tipo_descuento = models.CharField(max_length=15, choices=TIPO_DESCUENTO)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='promociones')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='promociones')
    canal = models.ForeignKey(CanalCliente, on_delete=models.CASCADE, related_name='promociones', null=True, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = "promociones.promocion"
        verbose_name = "Promoción"
        verbose_name_plural = "Promociones"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return self.nombre

class ReglaPromocion(TimeStampedModel):
    # ... (campos existentes, incluyendo ForeignKey a Promocion y Artículo/Grupo/Línea)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='reglas')
    articulo = models.ForeignKey(Articulo, on_delete=models.SET_NULL, null=True, blank=True,related_name='reglas_promocion')
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.SET_NULL, null=True, blank=True,related_name='reglas_promocion')
    linea = models.ForeignKey(LineaArticulo, on_delete=models.SET_NULL, null=True, blank=True,related_name='reglas_promocion')
    minimo_monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    minimo_cantidad = models.IntegerField(null=True, blank=True)
    maximo_cantidad = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "promociones.regla_promocion"
        verbose_name = "Regla de promoción"
        verbose_name_plural = "Reglas de promoción"

        def __str__(self):
            return f"Regla para {self.promocion.nombre}"

class ReglaEscala(TimeStampedModel):
    # ... (campos existentes, incluyendo ForeignKey a Promocion)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='escalas')
    articulo = models.ForeignKey(Articulo, on_delete=models.SET_NULL, null=True, blank=True, related_name='escalas_promocion')
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.SET_NULL, null=True, blank=True,related_name='escalas_promocion')
    linea = models.ForeignKey(LineaArticulo, on_delete=models.SET_NULL, null=True, blank=True,related_name='escalas_promocion')
    minimo_cantidad = models.IntegerField(null=True, blank=True)
    maximo_cantidad = models.IntegerField(null=True, blank=True)
    rango_inicio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rango_fin = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "promociones.regla_escala"
        verbose_name = "Escala de promoción"
        verbose_name_plural = "Escalas de promoción"

    def __str__(self):
        return f"Escala para {self.promocion.nombre} ({self.rango_inicio}-{self.rango_fin})"

class RecompensaPromocion(TimeStampedModel):
    # ... (campos existentes, incluyendo ForeignKey a ReglaPromocion/ReglaEscala)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regla = models.ForeignKey(ReglaPromocion, on_delete=models.CASCADE, null=True, blank=True,related_name='beneficios')
    escala = models.ForeignKey(ReglaEscala, on_delete=models.CASCADE, null=True, blank=True, related_name='beneficios')
    articulo = models.ForeignKey(Articulo, on_delete=models.SET_NULL, null=True, blank=True,related_name='beneficios_promocion')
    cantidad = models.IntegerField(null=True, blank=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "promociones.recompensa_promocion"
        verbose_name = "Recomensa de promoción"
        verbose_name_plural = "Recompesa de promoción"

    def __str__(self):
        regla_ref = self.regla.promocion.nombre if self.regla else self.escala.promocion.nombre if self.escala else "Sin referencia"
        return f"Beneficio para {regla_ref}"

class ReglaCompraConjunta(TimeStampedModel):
    # ... (campos existentes, incluyendo ForeignKey a Promocion)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='reglas_conjuntas')
    descuento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "promociones.regla_compra_conjunta"
        verbose_name = "Regla de compra conjunta"
        verbose_name_plural = "Reglas de compra conjunta"

    def __str__(self):
        return f"Regla conjunta para {self.promocion.nombre}"

class RequisitoCompraConjunta(TimeStampedModel):
    # ... (campos existentes, incluyendo ForeignKey a ReglaCompraConjunta)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regla_conjunta = models.ForeignKey(ReglaCompraConjunta, on_delete=models.CASCADE, related_name='requisitos')
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad_minima = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "promociones.requisito_compra_conjunta"
        verbose_name = "Requisito de compra conjunta"
        verbose_name_plural = "Requisitos de compra conjunta"

    def __str__(self):
        return f"{self.cantidad_minima} x {self.articulo.codigo_articulo}"

class ReglaProductosAcumulados(TimeStampedModel):
    # ... (campos existentes, incluyendo ForeignKey a Promocion y Grupo/Línea)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='reglas_acumuladas')
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.SET_NULL, null=True, blank=True)
    linea = models.ForeignKey(LineaArticulo, on_delete=models.SET_NULL, null=True, blank=True)
    minimo_cantidad_total = models.PositiveIntegerField()

    class Meta:
        db_table = "promociones.regla_productos_acumulados"
        verbose_name = "Regla de productos acumulados"
        verbose_name_plural = "Reglas de productos acumulados"

    def __str__(self):
        target = f"grupo {self.grupo.nombre_grupo}" if self.grupo else f"línea {self.linea.nombre_linea}" if self.linea else "productos seleccionados"
        return f"Acumulación de {target} (mín. {self.minimo_cantidad_total})"

class ArticuloAcumulable(TimeStampedModel):
    # ... (campos existentes, incluyendo ForeignKey a ReglaProductosAcumulados)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regla_acumulada = models.ForeignKey(ReglaProductosAcumulados, on_delete=models.CASCADE, related_name='articulos')
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)

    class Meta:
        db_table = "promociones.articulo_acumulable"
        verbose_name = "Artículo acumulable"
        verbose_name_plural = "Artículos acumulables"

    def __str__(self):
        return self.articulo.codigo_articulo

class RecompensaReglaAcumulada(TimeStampedModel):
    # ... (campos existentes, incluyendo ForeignKey a ReglaProductosAcumulados)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regla_acumulada = models.ForeignKey(ReglaProductosAcumulados, on_delete=models.CASCADE, related_name='beneficios')
    articulo = models.ForeignKey(Articulo, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField(null=True, blank=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "promociones.recompensa_regla_acumulada"
        verbose_name = "Recompensa de regla acumulada"
        verbose_name_plural = "Beneficios de regla acumulada"