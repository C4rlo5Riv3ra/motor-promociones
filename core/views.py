from django.shortcuts import render, redirect, get_object_or_404 
from django.core.paginator import Paginator 
from django.contrib.auth.decorators import login_required 
from .models import *
from django.views.decorators.http import require_POST
from django.contrib import messages

# Create your views here.
@login_required 
def articulos_list(request): 
    """Vista para listar artículos""" 
    articulos_list = Articulo.objects.all() 
    # Filtros (podrías expandir esto) 
    q = request.GET.get('q') 
    if q: 
        articulos_list = articulos_list.filter(descripcion__icontains=q) 
    # Paginación 
    paginator = Paginator(articulos_list, 15)  # 15 artículos por página 
    page_number = request.GET.get('page') 
    articulos = paginator.get_page(page_number) 
    context = { 
        'articulos': articulos, 
    } 
    return render(request, 'core/articulos/list.html', context)