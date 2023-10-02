import base64
import logging

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.exceptions import BadRequest
from user.serializers import UserReadSerializer
from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag
)

logger = logging.getLogger(__name__)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """[GET] Сериализатор для запроса (список тегов)."""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 1')
        return value


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для POST/PATCH запросов на создание рецептов.
    """
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True,
    )
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        required=True,
    )
    image = Base64ImageField(
        required=True,
        allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def _is_duplicated_items(self, initial_items: list, *args) -> bool:
        unique_items: set = set(initial_items)
        return len(initial_items) != len(unique_items)

    def _is_field_exists_and_clear(
        self,
        field: str,
        validated_data,
        instance
    ) -> list:
        if field in validated_data:
            items = validated_data.pop(field)
            if field == 'tags':
                instance.tags.clear()
            elif field == 'ingredients':
                instance.ingredients.clear()
            return items

    def _add_ingredients(self, recipe, ingredients) -> None:
        try:
            RecipeIngredient.objects.bulk_create(
                [
                    RecipeIngredient(
                        recipe=recipe,
                        ingredient=ingredient.get('id'),
                        amount=ingredient.get('amount'),
                    )
                    for ingredient in ingredients
                ]
            )
        except IntegrityError:
            raise ValidationError('Данный ингредиент уже есть в рецепте!')

    @transaction.atomic
    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.save()
        self._add_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = self._is_field_exists_and_clear(
            'tags',
            validated_data,
            instance)
        ingredients = self._is_field_exists_and_clear(
            'ingredients',
            validated_data,
            instance)
        super().update(instance, validated_data)
        instance.tags.set(tags)
        self._add_ingredients(instance, ingredients)
        instance.save()
        return instance

    def validate(self, data):
        # if not all(map(data.__contains__, ('tags', 'image', 'ingredients'))):
        #     logger.debug('not contains')
        #     raise BadRequest(
        #     'В запросе должны содержаться поля tags, image, ingredients.')
        if len(data['tags']) < 1:
            raise BadRequest('Количество тегов должно быть как минимум 1.')
        if len(data['name']) > settings.RECIPE_NAME_MAXLENGTH:
            raise serializers.ValidationError(
                'Длина названия должна быть не более 200 символов.'
            )
        if len(data['ingredients']) < 1:
            raise serializers.ValidationError(
                'В рецепте должен быть хотя бы один ингредиент.'
            )
        if data['cooking_time'] < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше или равно 1 минуте.'
            )
        if (
            self._is_duplicated_items(data['tags'])
            or self._is_duplicated_items(
                [item.get('id') for item in data['ingredients']]
            )
        ):
            logger.debug('Ууупппс, есть повторяющиеся элементы.')
            raise BadRequest(
                'В запросе есть повторяющиеся теги или ингредиаенты.')
        return data

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запроса получения списка рецептов."""
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = UserReadSerializer(
        read_only=True,
    )
    ingredients = RecipeIngredientReadSerializer(
        source='ingredients_used',
        many=True,
    )
    image = Base64ImageField(required=False, allow_null=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'image',
            'author',
            'ingredients',
            'name',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def is_obj_exists(self, model, obj):
        return (
            self.context.get('request').user.is_authenticated
            and model.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        )

    def get_is_favorited(self, obj):
        return self.is_obj_exists(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        return self.is_obj_exists(ShoppingCart, obj)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeReadShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'name',
            'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
        )
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message='Такой рецепт уже есть.'
            )
        ]


class ShoppingCartSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Такой рецепт уже есть.'
            )
        ]
