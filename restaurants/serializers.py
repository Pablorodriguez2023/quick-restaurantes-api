from rest_framework import serializers
from .models import Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            'id', 'name', 'address', 'rating', 'status', 'category', 
            'latitude', 'longitude', 'active', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'rating')

    def validate_rating(self, value):
        """
        Valida que el rating esté entre 0 y 5.
        """
        if value < 0 or value > 5:
            raise serializers.ValidationError("El rating debe estar entre 0 y 5.")
        return value
