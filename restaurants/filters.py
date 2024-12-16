import django_filters
from .models import Restaurant

class RestaurantFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.ChoiceFilter(choices=Restaurant.CATEGORY_CHOICES)
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    status = django_filters.CharFilter(field_name='status')

    class Meta:
        model = Restaurant
        fields = ['name', 'category', 'status', 'min_rating', 'max_rating']
