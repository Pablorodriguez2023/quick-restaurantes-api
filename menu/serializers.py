from rest_framework import serializers
from .models import MenuItem
from restaurants.serializers import RestaurantSerializer

class MenuItemSerializer(serializers.ModelSerializer):
    # Detalles del restaurante asociados al elemento del menú (opcionalmente se pueden excluir)
    restaurant_details = RestaurantSerializer(source='restaurant', read_only=True)

    class Meta:
        model = MenuItem
        fields = (
            'id', 
            'name', 
            'description', 
            'price', 
            'restaurant', 
            'restaurant_details', 
            'available', 
            'preparation_time',  
            'created_at', 
            'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'restaurant_details')

    def __init__(self, *args, **kwargs):
        """
        Permite incluir o excluir los detalles del restaurante según un parámetro de contexto.
        """
        include_details = kwargs.get('context', {}).get('include_details', True)
        super().__init__(*args, **kwargs)
        if not include_details:
            self.fields.pop('restaurant_details')

    def validate_restaurant(self, value):
        """
        Valida que el usuario autenticado tenga permiso para asociar un restaurante.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Debe estar autenticado para realizar esta acción.")
        
        # Si no es superusuario, verifica que el restaurante le pertenezca al usuario
        if not request.user.is_superuser and value.owner != request.user:
            raise serializers.ValidationError(
                "No puedes crear elementos del menú para un restaurante que no te pertenece."
            )
        return value
