from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from .models import Cart, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer
# Create your views here.


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += serializer.validated_data.get('quantity', 1)
            else:
                cart_item.quantity = serializer.validated_data.get('quantity', 1)
            cart_item.save()
            return Response({'message': 'Savatchaga qoshildi', 'status': status.HTTP_201_CREATED})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            return Response({"error": "Savatchangiz bo'sh"}, status=status.HTTP_400_BAD_REQUEST)
        
        address = request.data.get('address')
        if not address:
            return Response({"error": "Manzil kiritilmadi"}, status=status.HTTP_400_BAD_REQUEST)
        
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(user=user, total_price=total_price, address=address)
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
            
            cart_items.delete()
            
            return Response({"message": "Buyurtma qabul qilindi", "order_id": order.id}, status=status.HTTP_201_CREATED)