from django.db import models

class TipoCondicion(models.IntegerChoices):
    VOLUMEN = 1, 'Volumen de compra'
    MONTO = 2, 'Monto de compra'
    COMBINADO = 3, 'Condición combinada'

class TipoAccion(models.IntegerChoices):
    DESCUENTO = 1, 'Descuento'
    BONIFICACION = 2, 'Bonificación'
    COMBO = 3, 'Combinación'

class EstadoEntidades(models.IntegerChoices):
    ACTIVO = 1, 'Activo'
    DE_BAJA = 2, 'De baja'

class EstadoOrden(models.IntegerChoices): 
    PENDIENTE = 1, "Pendiente" 
    PROCESANDO = 2, "Procesando" 
    COMPLETADA = 3, "Completada" 
    CANCELADA = 4, "Cancelada" 

class TipoAfectacion(models.IntegerChoices):
    AFECTADO = 1, 'Afectado'
    NO_AFECTADO = 2, 'No afectado'
    NULL = 3, 'Ninguno'