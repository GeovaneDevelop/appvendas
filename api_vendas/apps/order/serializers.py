from django.db import models

from rest_framework import serializers
from .models import Order, OrderItem

from apps.produtos.models import Produtos


class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.StringRelatedField(source='product')
    img = serializers.StringRelatedField(source='product.foto')
    total_item = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'price', 'product', 'img', 'product_name', 'total_item']

    def get_total_item(self, obj):
        return obj.price * obj.quantity    


class OrderSerializer(serializers.ModelSerializer):

    client = serializers.StringRelatedField(source='client.name')
    items = OrderItemSerializer(required=False, many=True)
    total_order = serializers.SerializerMethodField()
            
    class Meta:
        model = Order
        fields = ['id', 'status', 'client', 'created_at', 'update_at', 'total_order', 'obs', 'items',]

    
    def get_total_order(self, obj):
        aggregate_queryset = obj.items.aggregate(
            total=models.Sum(
                models.F('price') * models.F('quantity'),
                output_field=models.DecimalField()
            )
        )
        return aggregate_queryset['total']

    def create(self, validated_data):
        items_data = {}
        if validated_data.get("items"):
            items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        order.save()

        return order
