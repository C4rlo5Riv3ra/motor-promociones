from django.contrib import admin

# Register your models here.

from .models import Articulo, Cliente, CanalCliente

admin.site.register(Articulo)
admin.site.register(CanalCliente)
admin.site.register(Cliente)