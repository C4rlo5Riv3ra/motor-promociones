from django.db import models

class ESTADO_ENTIDADES(models.IntegerChoices):
    ACTIVO = 1, 'Activo'
    DE_BAJA = 2, 'De baja'

class TIPO_IDENTIFICACION(models.TextChoices):
    DNI = 'D', 'DNI'
    RUC = 'R', 'RUC',
    CE = 'C', 'CE',
    PASAPORTE = 'P', 'Pasaporte'