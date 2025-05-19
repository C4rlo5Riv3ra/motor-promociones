from django.http import HttpResponse
from django.shortcuts import render,        redirect
from django.db.models import Sum

# Create your views here.
from rest_framework import viewsets
from .forms import PedidoSimuladoForm
from core.models import Articulo, Cliente
from datetime import date
from collections import defaultdict




from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from django.urls import reverse, reverse_lazy


from .models import Promocion, CondicionPromocion, RangoCondicion, Bonificacion, Descuento
from .serializers import (
    PromocionSerializer,
    CondicionPromocionSerializer,
    RangoCondicionSerializer,
    BonificacionSerializer,
    DescuentoSerializer
)

def evaluar_promocion_view(request):
    if request.method == 'POST':
        form = PedidoSimuladoForm(request.POST)
        if form.is_valid():
            cliente = form.cleaned_data['cliente']
            articulos = form.cleaned_data['articulos']

            promociones = Promocion.objects.filter(
                canal_cliente=cliente.canal,
                estado=1,
                fecha_inicio__lte=date.today(),
                fecha_fin__gte=date.today()
            )

            promociones_aplicadas = []

            for promo in promociones:
                condiciones = promo.condiciones.all()
                bonificaciones_aplicadas = []
                descuentos_aplicados = []

                for cond in condiciones:
                    # Suposición simple: cada artículo seleccionado equivale a 1 unidad
                    # (esto se debe mejorar en el futuro con cantidades reales)
                    cantidad = articulos.filter(pk=cond.articulo.pk).count() if cond.articulo else 0
                    monto_estimado = cantidad * 10  # Suposición: cada artículo cuesta S/10

                    cumple_condicion = False
                    veces = 1

                    if not cond.rango_escalado:
                        # Evaluación simple
                        if cond.cantidad_minima and cantidad >= cond.cantidad_minima:
                            cumple_condicion = True
                            veces = cantidad // cond.cantidad_minima
                        elif cond.monto_minimo and monto_estimado >= cond.monto_minimo:
                            cumple_condicion = True
                            veces = int(monto_estimado // cond.monto_minimo)

                        if cumple_condicion:
                            if promo.tipo_promocion in ['BONI', 'COMBI']:
                                bonis = Bonificacion.objects.filter(promocion=promo, condicion=cond)
                                for b in bonis:
                                    b.cantidad *= veces
                                    bonificaciones_aplicadas.append(b)

                            if promo.tipo_promocion in ['DESC', 'COMBI']:
                                descs = Descuento.objects.filter(promocion=promo, condicion=cond)
                                descuentos_aplicados.extend(descs)

                    else:
                        # Evaluación por rangos escalados
                        rangos = cond.rangos.all().order_by('minimo')
                        valor_base = monto_estimado if promo.condicion_base == 'MONTO' else cantidad

                        for r in rangos:
                            if (r.maximo is None and valor_base >= r.minimo) or (r.minimo <= valor_base <= r.maximo):
                                if promo.tipo_promocion in ['BONI', 'COMBI']:
                                    bonis = Bonificacion.objects.filter(promocion=promo, rango=r)
                                    bonificaciones_aplicadas.extend(bonis)

                                if promo.tipo_promocion in ['DESC', 'COMBI']:
                                    descs = Descuento.objects.filter(promocion=promo, rango=r)
                                    descuentos_aplicados.extend(descs)
                                break

                if bonificaciones_aplicadas or descuentos_aplicados:
                    promociones_aplicadas.append({
                        'promocion': promo,
                        'bonificaciones': bonificaciones_aplicadas,
                        'descuentos': descuentos_aplicados
                    })

            return render(request, 'promotion/resultado_promocion.html', {
                'promociones_aplicadas': promociones_aplicadas
            })
    else:
        form = PedidoSimuladoForm()

    return render(request, 'promotion/pedido_form.html', {'form': form})









# DASHBOARD
class DashboardView(TemplateView):
    template_name = 'promotion/dashboard.html'

# PROMOCIONES
class PromocionListView(ListView):
    model = Promocion
    template_name = 'promotion/promocion_list.html'
    context_object_name = 'promociones'

class PromocionCreateView(CreateView):
    model = Promocion
    fields = '__all__'
    template_name = 'promotion/promocion_form.html'
    success_url = reverse_lazy('promocion_list')

class PromocionUpdateView(UpdateView):
    model = Promocion
    fields = '__all__'
    template_name = 'promotion/promocion_form.html'
    success_url = reverse_lazy('promocion_list')

class PromocionDeleteView(DeleteView):
    model = Promocion

    def get_success_url(self):
        return reverse('promocion_list')

# CONDICIONES
from django.shortcuts import get_object_or_404
from .models import Promocion, CondicionPromocion
class CondicionListView(ListView):
    model = CondicionPromocion
    template_name = 'promotion/condicion_list.html'
    context_object_name = 'condiciones'

    def get_queryset(self):
        promocion_id = self.kwargs['promocion_id']
        return CondicionPromocion.objects.filter(promocion__promocion_id=promocion_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        promocion_id = self.kwargs['promocion_id']
        context['promocion'] = get_object_or_404(Promocion, promocion_id=promocion_id)
        return context
class CondicionCreateView(CreateView):
    model = CondicionPromocion
    fields = ['articulo', 'linea', 'monto_minimo', 'cantidad_minima', 'rango_escalado']
    template_name = 'promotion/condicion_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.promocion = get_object_or_404(Promocion, promocion_id=kwargs['promocion_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.promocion = self.promocion
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['promocion'] = self.promocion 
        return context

    def get_success_url(self):
        return reverse('condicion_list', kwargs={'promocion_id': self.promocion.promocion_id})



class CondicionUpdateView(UpdateView):
    model = CondicionPromocion
    fields = '__all__'
    template_name = 'promotion/condicion_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['promocion'] = self.object.promocion
        return context

    def get_success_url(self):
        return reverse('condicion_list', kwargs={'promocion_id': self.object.promocion.promocion_id})
    
class CondicionDeleteView(DeleteView):
    model = CondicionPromocion

    def get_success_url(self):
        return reverse('condicion_list', kwargs={'promocion_id': self.object.promocion.promocion_id})










# RANGOS
class RangoListView(ListView):
    model = RangoCondicion
    template_name = 'promotion/condicion_list.html'  # puedes hacer un rango_list.html si prefieres
    context_object_name = 'rangos'

class RangoCreateView(CreateView):
    model = RangoCondicion
    fields = '__all__'
    template_name = 'promotion/rango_form.html'

    def get_success_url(self):
        return reverse_lazy('rango_lista_general')

# BONIFICACIONES
class BonificacionListView(ListView):
    model = Bonificacion
    template_name = 'promotion/condicion_list.html'
    context_object_name = 'bonificaciones'

class BonificacionCreateView(CreateView):
    model = Bonificacion
    fields = '__all__'
    template_name = 'promotion/bonificacion_form.html'

    def get_success_url(self):
        return reverse_lazy('bonificacion_lista_general')

# DESCUENTOS
class DescuentoListView(ListView):
    model = Descuento
    template_name = 'promotion/condicion_list.html'
    context_object_name = 'descuentos'

class DescuentoCreateView(CreateView):
    model = Descuento
    fields = '__all__'
    template_name = 'promotion/descuento_form.html'

    def get_success_url(self):
        return reverse_lazy('descuento_lista_general')













class PromocionViewSet(viewsets.ModelViewSet):
    queryset = Promocion.objects.all()
    serializer_class = PromocionSerializer

class CondicionPromocionViewSet(viewsets.ModelViewSet):
    queryset = CondicionPromocion.objects.all()
    serializer_class = CondicionPromocionSerializer

class RangoCondicionViewSet(viewsets.ModelViewSet):
    queryset = RangoCondicion.objects.all()
    serializer_class = RangoCondicionSerializer

class BonificacionViewSet(viewsets.ModelViewSet):
    queryset = Bonificacion.objects.all()
    serializer_class = BonificacionSerializer

class DescuentoViewSet(viewsets.ModelViewSet):
    queryset = Descuento.objects.all()
    serializer_class = DescuentoSerializer