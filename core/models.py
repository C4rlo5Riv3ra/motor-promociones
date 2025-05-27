from django.db import models
from promotion_engine.choices import ESTADO_ENTIDADES, TIPO_IDENTIFICACION
import uuid

# Create your models here.

class Empresa(models.Model):
    id = models.CharField(primary_key=True)
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


class GrupoArticulo(models.Model):
    grupo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='grupos_articulos')
    codigo_grupo = models.CharField(max_length=5, null=False)
    nombre_grupo = models.CharField(max_length=150, null=False)
    estado = models.IntegerField(choices=ESTADO_ENTIDADES, default=ESTADO_ENTIDADES.ACTIVO)

    class Meta:
        db_table = "productos.grupos_articulos"
        ordering = ["codigo_grupo"]

    def __str__(self):
        return self.nombre_grupo


class LineaArticulo(models.Model):
    linea_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='lineas_articulos')
    codigo_linea = models.CharField(max_length=10, null=False)
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.CASCADE,related_name='lineas')
    nombre_linea = models.CharField(max_length=100)
    estado = models.SmallIntegerField(choices=ESTADO_ENTIDADES, default=ESTADO_ENTIDADES.ACTIVO)

    class Meta:
        db_table = "productos.linea_articulo"
        verbose_name = "Línea de artículo"
        verbose_name_plural = "Líneas de artículos"

    def __str__(self):
        return self.nombre_linea


class Articulo(models.Model):
    articulo_id = models.UUIDField(primary_key=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='articulos')
    codigo_articulo = models.CharField(max_length=200, unique=True)
    codigo_barras = models.CharField(max_length=200, null=True, blank=True)
    codigo_ean = models.CharField(max_length=200, null=True, blank=True)
    descripcion = models.CharField(max_length=150)
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.RESTRICT)
    linea = models.ForeignKey(LineaArticulo, on_delete=models.RESTRICT)
    unidad_medida = models.CharField(max_length=10, null=True, blank=True)
    unidad_compra = models.CharField(max_length=10, null=True, blank=True)
    unidad_reparto = models.CharField(max_length=10, null=True, blank=True)
    unidad_bonificacion = models.CharField(max_length=10, null=True, blank=True)
    factot_reparto = models.IntegerField(null=True, blank=True)
    factor_compra = models.IntegerField(null=True, blank=True)
    factor_bonificacion = models.IntegerField(null=True, blank=True)
    tipo_afectacion = models.CharField(max_length=10, null=True, blank=True)
    peso = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tipo_producto = models.IntegerField(max_length=10, null=True, blank=True)
    afecto_retencion = models.CharField(max_length=10, null=True, blank=True)
    afecto_detraccion = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = "productos.articulo"
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ["codigo_articulo"]

    def __str__(self):
        return f"{self.codigo_articulo} - {self.descripcion}"


class CanalCliente(models.Model):
    canal_id = models.CharField(max_length=3, primary_key=True)
    nombre_canal = models.CharField(max_length=100)

    class Meta:
        db_table = "productos.canal_cliente"
        verbose_name = "Canal de cliente"
        verbose_name_plural = "Canales de clientes"

    def __str__(self):
        return self.nombre_canal


class Cliente(models.Model):
    cliente_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_identificacion = models.CharField(max_length=1, choices=TIPO_IDENTIFICACION)
    nro_identificacion = models.CharField(max_length=20)
    nombres = models.CharField(max_length=150)
    direccion = models.CharField(max_length=150, blank=True, null=True)
    correo_electronico = models.EmailField(max_length=255, blank=True, null=True)
    nro_movil = models.CharField(max_length=15, blank=True, null=True)
    estado = models.SmallIntegerField(choices=ESTADO_ENTIDADES, default=ESTADO_ENTIDADES.ACTIVO)
    canal = models.ForeignKey(CanalCliente, on_delete=models.CASCADE)

    class Meta:
        db_table = "productos.cliente"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        unique_together = [['tipo_identificacion', 'nro_identificacion']]

    def __str__(self):

        return f"{self.nombres} ({self.get_tipo_identificacion_display()}: {self.nro_identificacion})"



class Sucursal(models.Model):
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
