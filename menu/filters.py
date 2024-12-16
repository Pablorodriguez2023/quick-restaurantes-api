import django_filters
from .models import MenuItem

class MenuItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    restaurant = django_filters.NumberFilter(field_name='restaurant__id')
    category = django_filters.CharFilter(field_name='category')
    available = django_filters.BooleanFilter()

    class Meta:
        model = MenuItem
        fields = ['name', 'category', 'available', 'min_price', 'max_price', 'restaurant']
