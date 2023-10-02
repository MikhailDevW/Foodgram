import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.exceptions import BadRequest
from api.paginators import CustomPaginator
from .filters import RecipeFilter
from .models import (
    Favorite, Ingredient, RecipeIngredient, Recipe,
    ShoppingCart, Tag
)
from .permissions import IsAuthorOrAdmin
from .serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeReadSerializer,
    RecipeReadShortSerializer, RecipeCreateUpdateSerializer,
    ShoppingCartSerializer, TagSerializer
)
from .services import get_report

logger = logging.getLogger(__name__)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Работа с рецептами.
    GET /recipes/ - Страница доступна всем пользователям.
    Доступна фильтрация по избранному, автору, списку покупок и тегам.
    POST /reipes/ - Доступно только авторизованному пользователю.
    UPDATE /recipes/ - доступной только автору.
    DELETE /recipes/ - доступной только автору.
    """
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def _get_object_or_400(self, model, *args, **kwargs):
        try:
            return model.objects.get(**kwargs)
        except ObjectDoesNotExist:
            raise BadRequest()

    def _add_item(self, serializer, request, **kwargs) -> Response:
        recipe = self._get_object_or_400(Recipe, id=kwargs['pk'])
        serializer = serializer(
            data={
                'user': request.user.id,
                'recipe': int(kwargs['pk']), },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            RecipeReadShortSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    def _delete_item(self, model, request, **kwargs) -> Response:
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        self._get_object_or_400(
            model,
            user=request.user,
            recipe=recipe,
        )
        model.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        return queryset

    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = (permissions.AllowAny,)
        elif self.action == 'create':
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.action == 'partial_update' or self.action == 'destroy':
            self.permission_classes = (IsAuthorOrAdmin, )
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateUpdateSerializer
        return RecipeReadSerializer

    @action(
        detail=False,
        methods=['GET', ],
        permission_classes=(permissions.IsAuthenticated, ),
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request, **kwargs):
        """
        Скачать список покупок
        Скачать файл со списком покупок. Это может быть TXT/PDF/CSV.
        Доступно только авторизованным пользователям.
        """

        ingrediend_list = RecipeIngredient.objects.filter(
            recipe__shoppings__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit',
        ).annotate(
            amount=Sum('amount')
        )
        return get_report(ingrediend_list)

    @action(
        detail=True,
        methods=['POST', 'DELETE', ],
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated, ),
    )
    def shopping_cart(self, request, **kwargs):
        """
        Добавить рецепт в список покупок.
        Доступно только авторизованным пользователям.
        """
        if request.method == 'POST':
            return self._add_item(ShoppingCartSerializer, request, **kwargs)
        return self._delete_item(ShoppingCart, request, **kwargs)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated, ),
    )
    def favorite(self, request, **kwargs):
        """
        Добавить рецепт в к себе в избранное.
        Доступно только авторизованному пользователю.
        """
        if request.method == 'POST':
            return self._add_item(FavoriteSerializer, request, **kwargs)
        return self._delete_item(Favorite, request, **kwargs)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /tags/ - список тегов приложения.
    Только гет запросы.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Список ингредиентов.
    Список ингредиентов с возможностью поиска по имени.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ['^name', ]
