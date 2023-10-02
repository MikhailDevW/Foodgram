import logging

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .validators import slug_validator
from user.models import CustomUser

MIN_COOKING_TIME = 1
NAME_MAX_LENGTH = 200
SLUG_MAX_LENGTH = 200
COLOR_MAX_LENGTH = 7

logger = logging.getLogger(__name__)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients_used',
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        'Кол-во',
        validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Состав'
        verbose_name_plural = 'Составы'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            )
        ]


class Recipe(models.Model):
    """Модель рецептов приложения."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    name = models.CharField(
        'Название',
        max_length=settings.RECIPE_NAME_MAXLENGTH,
    )
    image = models.ImageField(
        upload_to='images/',
        blank=True, null=True,
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        'Ingredient',
        through=RecipeIngredient,
    )
    tags = models.ManyToManyField(
        'Tag',
    )
    cooking_time = models.PositiveIntegerField(
        'Время',
        validators=[MinValueValidator(1), ]
    )
    pub_date = models.DateField(
        'Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Модель тегов для рецептов."""
    name = models.CharField(
        'Имя тега',
        max_length=settings.TAG_MODEL_SETTINGS.get(
            'name_max_length', NAME_MAX_LENGTH,
        ),
    )
    color = models.CharField(
        'Цвет тега в HEX',
        max_length=settings.TAG_MODEL_SETTINGS.get(
            'color_max_length', COLOR_MAX_LENGTH,
        ),
    )
    slug = models.SlugField(
        'Слаг',
        max_length=settings.TAG_MODEL_SETTINGS.get(
            'slug_max_length', SLUG_MAX_LENGTH,
        ),
        unique=True,
        validators=[slug_validator, ],
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингридиентов для рецептов."""
    name = models.CharField(
        'Ингредиент',
        max_length=NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        'Ед. измерения',
        max_length=100,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shoppings',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppings',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
