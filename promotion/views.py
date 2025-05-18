from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from promotion.serializer import PedidoEvaluacionSerializer, PromocionSerializer
from promotion.services import calcular_promociones

# Create your views here.

class EvaluarPromocionesView(APIView):
    def post(self, request):
        serializer = PedidoEvaluacionSerializer(data=request.data)
        if serializer.is_valid():
            pedido_data = serializer.validated_data
            
            # Lógica para calcular promociones (implementar en services.py)
            promociones_aplicables = calcular_promociones(pedido_data)
            
            # Serializar el resultado
            serializer_resultado = PromocionSerializer(
                promociones_aplicables, 
                many=True, 
                context={'request': request}
            )
            return Response(serializer_resultado.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)