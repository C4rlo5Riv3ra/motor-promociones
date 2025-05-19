from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Pedido
from .serializers import PedidoSerializer

class PedidoListView(APIView):
    def get(self, request):
        pedidos = Pedido.objects.all().order_by('-created_at')
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)
