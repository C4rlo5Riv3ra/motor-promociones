from django.db import models
import uuid
from core.models import TimeStampedModel, Cliente, Articulo, GrupoArticulo, LineaArticulo, CanalCliente, ESTADO_ENTIDADES

class TipoPromocion:
    ESCALAS = 'ESCALAS'
    NORMAL = 'NORMAL'
    CONJUNTA = 'CONJUNTA'
    ACUMULADA = 'ACUMULADA'

    CHOICES = [
        (ESCALAS, 'Escalas'),
        (NORMAL, 'Normal'),
        (CONJUNTA, 'Compra Conjunta'),
        (ACUMULADA, 'Productos Acumulados'),
    ]

class TipoDescuento:
    BONIFICACION = 'BONIFICACION'
    DESCUENTO = 'DESCUENTO'
    MIXTO = 'MIXTO'

    CHOICES = [
        (BONIFICACION, 'Bonificación'),
        (DESCUENTO, 'Descuento'),
        (MIXTO, 'Mixto')
    ]


class Empresa(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    razon_social = models.CharField(max_length=255)
    ruc = models.CharField(max_length=15, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "promociones.empresa"
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Sucursal(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='sucursales')
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "promociones.sucursal"
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"


class Promocion(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    tipo_promocion = models.CharField(max_length=15, choices=TipoPromocion.CHOICES)
    tipo_descuento = models.CharField(max_length=15, choices=TipoDescuento.CHOICES)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='reglas')
    articulo = models.ForeignKey(Articulo, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reglas_promocion')
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='reglas_promocion')
    linea = models.ForeignKey(LineaArticulo, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='reglas_promocion')
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='escalas')
    articulo = models.ForeignKey(Articulo, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='escalas_promocion')
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='escalas_promocion')
    linea = models.ForeignKey(LineaArticulo, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='escalas_promocion')
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regla = models.ForeignKey(ReglaPromocion, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='beneficios')
    escala = models.ForeignKey(ReglaEscala, on_delete=models.CASCADE, null=True, blank=True, related_name='beneficios')
    articulo = models.ForeignKey(Articulo, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='beneficios_promocion')
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='reglas_conjuntas')
    descuento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "promociones.regla_compra_conjunta"
        verbose_name = "Regla de compra conjunta"
        verbose_name_plural = "Reglas de compra conjunta"

    def __str__(self):
        return f"Regla conjunta para {self.promocion.nombre}"


class RequisitoCompraConjunta(models.Model):
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


class ArticuloAcumulable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regla_acumulada = models.ForeignKey(ReglaProductosAcumulados, on_delete=models.CASCADE, related_name='articulos')
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)

    class Meta:
        db_table = "promociones.articulo_acumulable"
        verbose_name = "Artículo acumulable"
        verbose_name_plural = "Artículos acumulables"

    def __str__(self):
        return self.articulo.codigo_articulo


class RecompensaReglaAcumulada(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regla_acumulada = models.ForeignKey(ReglaProductosAcumulados, on_delete=models.CASCADE, related_name='beneficios')
    articulo = models.ForeignKey(Articulo, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField(null=True, blank=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "promociones.recompensa_regla_acumulada"
        verbose_name = "Recompensa de regla acumulada"
        verbose_name_plural = "Beneficios de regla acumulada"