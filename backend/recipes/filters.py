from django_filters.rest_framework import FilterSet, filters

from .models import Recipe, Tag


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', )

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shoppings__user=user)
        return queryset
