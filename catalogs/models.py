from django.db import models
from django.contrib.auth.hashers import make_password
from promotion_engine.choices import *
import uuid

# Create your models here.

class Empresa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = "empresa"
        ordering = ['id']

class Sucursal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "sucursal"
        ordering = ['id']

class GrupoArticulo(models.Model):
    grupo_id = models.UUIDField(primary_key=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.RESTRICT, null=False, related_name='empresa_grupo')
    codigo_grupo = models.CharField(max_length=5, null=False)
    nombre_grupo = models.CharField(max_length=150, null=False)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)

    def __str__(self):
        return self.nombre_grupo

    class Meta:
        db_table = "grupos_articulos"
        ordering = ["codigo_grupo"]

class LineaArticulo(models.Model):
    linea_id = models.UUIDField(primary_key=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.RESTRICT, null=False, related_name='empresa_linea')
    codigo_linea = models.CharField(max_length=10, null=False)
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.RESTRICT, null=False, related_name='grupo_linea')
    nombre_linea = models.CharField(max_length=150, null=False)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)

    def __str__(self):
        return self.nombre_linea

    class Meta:
        db_table = "lineas_articulos"
        ordering = ["codigo_linea"]

class Articulo(models.Model):
    articulo_id = models.UUIDField(primary_key=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.RESTRICT, null=False, related_name='empresa_articulo')
    codigo_articulo = models.CharField(max_length=200)
    codigo_barras = models.CharField(max_length=200, null=True, blank=True)
    codigo_ean = models.CharField(max_length=200, null=True, blank=True)
    descripcion = models.CharField(max_length=150)
    presentacion = models.CharField(max_length=100, null=True)
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.RESTRICT)
    linea = models.ForeignKey(LineaArticulo, on_delete=models.RESTRICT)
    unidad_medida = models.CharField(max_length=10, null=True)
    unidad_compra = models.CharField(max_length=10, null=True)
    unidad_reparto = models.CharField(max_length=10, null=True)
    unidad_bonificacion = models.CharField(max_length=10, null=True)
    factor_reparto = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    factor_compra = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    factor_bonificacion = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    tipo_afectacion = models.CharField(max_length=10, null=True) # en choices es 1
    peso = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    tipo_producto = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)
    afecto_retencion = models.CharField(max_length=10, null=True) # en choices es N
    afecto_detraccion = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.descripcion

    class Meta:
        db_table = "articulos"

class ListaPrecio(models.Model):
    articulo = models.UUIDField(primary_key=True)
    precio_1 = models.DecimalField(max_digits=12, decimal_places=2)
    precio_2 = models.DecimalField(max_digits=12, decimal_places=2)
    precio_3 = models.DecimalField(max_digits=12, decimal_places=2)
    precio_4 = models.DecimalField(max_digits=12, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2)
    precio_costo = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "lista_precios"

    def __str__(self):
        return self.articulo.descripcion

class CanalCliente(models.Model):
    canal_id = models.UUIDField(primary_key=True)
    nombre_canal = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.nombre_canal

    class Meta:
        db_table = 'canal_cliente'
        ordering = ['canal_id']

class TipoIdentificacion(models.Model):
    tipo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=5, null=False, unique=True)
    descripcion = models.CharField(max_length=100, null=False)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)

    def __str__(self):
        return self.descripcion

    class Meta:
        db_table = "tipo_identificacion"
        ordering = ["tipo_id"]

# --- Usuarios y personas ---

class Usuario(models.Model):
    usuario_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_usuario = models.CharField(max_length=150, null=False)
    correo = models.EmailField(max_length=255, unique=True, null=False)
    contrasena = models.CharField(max_length=128, null=False)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.contrasena.startswith('pbkdf2_'):
            self.contrasena = make_password(self.contrasena)
        super().save(*args, **kwargs)

    class Meta:
        db_table = "usuario"
        ordering = ["usuario_id"]

class Vendedor(models.Model):
    vendedor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_id = models.ForeignKey(TipoIdentificacion, on_delete=models.RESTRICT, null=False, related_name='vendedores', db_column='tipo_id')
    nro_identificacion = models.CharField(max_length=18, null=False)
    nombres = models.CharField(max_length=250, null=False)
    direccion = models.CharField(max_length=150, null=False)
    correo = models.EmailField(max_length=255, unique=True, null=False)
    nro_movil = models.CharField(max_length=20, null=True)
    canal_id = models.ForeignKey(CanalCliente, on_delete=models.RESTRICT, null=False, related_name='vendedor_canal', db_column='canal_id')
    supervisor = models.CharField(max_length=150, null=True)
    territorio = models.CharField(max_length=5, null=True)
    rol_id = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=False, related_name='vendedor_usuario', db_column='rol_id')

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    class Meta:
        db_table = "vendedor"
        ordering = ["vendedor_id"]

class Cliente(models.Model):
    cliente_id = models.UUIDField(primary_key=True)
    tipo_id = models.ForeignKey(TipoIdentificacion, on_delete=models.RESTRICT, null=False, related_name='clientes', db_column='tipo_id')
    nro_identificacion = models.CharField(max_length=12, null=False)
    nombres = models.CharField(max_length=150, null=False)
    direccion = models.CharField(max_length=150, null=False)
    correo_electronico = models.CharField(max_length=255, null=False)
    nro_movil = models.CharField(max_length=15, null=False)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)
    canal_id = models.ForeignKey(CanalCliente, on_delete=models.RESTRICT, null=False, related_name='cliente_canal', db_column='canal_id')

    def __str__(self):
        return self.nombres

    class Meta:
        db_table = 'cliente'
        ordering = ['cliente_id']

