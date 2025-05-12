from django.db import models

class TipoCondicion(models.IntegerChoices):
    VOLUMEN = 1, 'Volumen de compra'
    MONTO = 2, 'Monto de compra'
    COMBINADO = 3, 'Condición combinada'

class TipoAccion(models.IntegerChoices):
    DESCUENTO = 1, 'Descuento'
    BONIFICACION = 2, 'Bonificación'
    COMBO = 3, 'Combinación'
