from django.db import models

class ESTADO_ENTIDADES(models.IntegerChoices):
    ACTIVO = 1, 'Activo'
    DE_BAJA = 2, 'De baja'

class TIPO_IDENTIFICACION(models.TextChoices):
    DNI = 'D', 'DNI'
    RUC = 'R', 'RUC',
    CE = 'C', 'CE',
    PASAPORTE = 'P', 'Pasaporte'

class TipoPromocion(models.TextChoices):
    BONIFICACION = 'BONI', 'Bonificación'
    DESCUENTO = 'DESC', 'Descuento'
    COMBINADA = 'COMB', 'Combinada'

class TipoCondicion(models.TextChoices):
    MONTO = 'MONTO', 'Por Monto'
    CANTIDAD = 'CANTIDAD', 'Por Cantidad'
    COMBINADA = 'COMBI', 'Combinada'
