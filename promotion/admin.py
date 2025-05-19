from django.contrib import admin
from .models import (
    Promocion,
    CondicionPromocion,
    RangoCondicion,
    Bonificacion,
    Descuento,
)

admin.site.register(Promocion)
admin.site.register(CondicionPromocion)
admin.site.register(RangoCondicion)
admin.site.register(Bonificacion)
admin.site.register(Descuento)
