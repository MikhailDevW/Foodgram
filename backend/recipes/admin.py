from django.contrib import admin
from django.contrib.admin import StackedInline

from . import models

EXTRA_FIELDS_IN_RECIPE = 1
MIN_INGREDIENT_AMOUNT = 1


class IngredientInline(StackedInline):
    model = models.RecipeIngredient
    extra = EXTRA_FIELDS_IN_RECIPE
    min_num = MIN_INGREDIENT_AMOUNT

    verbose_name = 'Ингредиент'


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    list_editable = ('color', )
    list_filter = ('name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_editable = ('measurement_unit', )
    list_filter = ('name', )
    search_fields = ('name', )
    empty_value_display = '-пусто-'


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'pub_date',
        'count',
    )
    list_filter = ('name', )
    list_editable = ('name', )
    search_fields = ('name', 'author__username', 'tags__name')
    empty_value_display = '-пусто-'
    readonly_fields = ('pub_date', )

    def count(self, obj) -> int:
        return obj.favorites.count()

    count.short_description = 'В избранном'

    save_on_top = True
    inlines = (IngredientInline,)
    date_hierarchy = 'pub_date'


@admin.register(models.RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
