from django import forms
from core.models import Cliente, Articulo


class PedidoSimuladoForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), label="Cliente")
    articulos = forms.ModelMultipleChoiceField(
        queryset=Articulo.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Artículos"
    )
