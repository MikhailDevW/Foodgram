import logging

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers, status
from rest_framework.fields import SerializerMethodField
from rest_framework.response import Response

from recipes.models import Recipe
from .models import CustomUser

logger = logging.getLogger(__name__)


def check_new_password(data):
    return (
        data['current_password'] == data['new_password']
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


class SubscribtionsSerializer(serializers.ModelSerializer):
    """Работа с подписками."""
    is_subscribed = SerializerMethodField()

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    id = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes_limit = self.context.get(
            'request',
            None
        ).get('recipes_limit', None)
        logger.debug(obj)
        recipes = obj.recipe.all()
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        serializer = RecipeReadShortSerializer(
            recipes,
            many=True,
            read_only=True,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipe.count()

    def get_is_subscribed(self, obj):
        return False

    def validate(self, attrs):
        user = self.context['user']
        sub_user = self.context['sub_user']
        if (
            int(sub_user.id) == user.id
            or CustomUser.objects.filter(subscribes=sub_user).exists()
        ):
            return Response(
                {'detail': 'нельзя подписаться на самого себя'
                 'или на существующего в подписках пользователя', },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().validate(attrs)


class UserReadSerializer(serializers.ModelSerializer):
    """Получение пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return False


class SetPasswordSerializer(serializers.Serializer):
    """Изменение пароля пользователя."""
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        try:
            validate_password(data['new_password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )
        is_valid = self.context['request'].user.check_password(
            data['current_password']
        )
        if not is_valid:
            raise serializers.ValidationError()
        return data
