import logging

from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.paginators import CustomPaginator
from .models import CustomUser
from .serializers import (
    SetPasswordSerializer,
    SubscribtionsSerializer,
    UserReadSerializer)

logger = logging.getLogger(__name__)


class CustomUserViewSet(UserViewSet):
    """
    Работа с пользователями приложения.
    Список пользователей и профиль доступны всем.
    [GET | {id}] - получение всех пользователей или конкретного.
    [POST] - регистрация пользователя.
    [GET/'me'] - профиль текущего пользователя.
    [POST/'set_password'] - изменения пароля.
    """
    pagination_class = CustomPaginator

    def get_queryset(self):
        queryset = CustomUser.objects.prefetch_related('subscribes').all()
        return queryset

    def get_permissions(self):
        if self.action in ('list', 'create', 'retrieve'):
            self.permission_classes = (permissions.AllowAny, )
        else:
            self.permission_classes = (permissions.IsAuthenticated, )
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'me']:
            return UserReadSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated, ),
        url_path='subscriptions',
        pagination_class=CustomPaginator,
    )
    def subscriptions(self, request, *args, **kwargs):
        """
        [GET] - Возвращает пользователей, на которых подписан текущий юзер.
        В выдачу добавляются рецепты.
        """
        subscribes = self.request.user.subscribes.all()
        page = self.paginate_queryset(subscribes)

        serializer = SubscribtionsSerializer(
            page,
            many=True,
            context={"request": request.query_params},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE', ],
        permission_classes=(permissions.IsAuthenticated, ),
        url_path='subscribe',
    )
    def subscribe(self, request, id):
        """
        Дополнительная ручка для подписки на другого пользователя.
        Нам прилетает id и мы на него подписываемся.
        [POST] - подписываемся на другого пользователя.
        [DELETE] - отписываемся от пользователя
        """
        user = self.request.user
        sub_user = get_object_or_404(CustomUser, id=id)
        logger.debug(request.query_params)
        if request.method == 'POST':
            serializer = SubscribtionsSerializer(
                sub_user,
                context={
                    'request': request.query_params,
                    'user': user,
                    'sub_user': sub_user,
                },
            )
            user.subscribes.add(sub_user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if sub_user not in user.subscribes.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.subscribes.remove(sub_user)
        return Response(status=status.HTTP_204_NO_CONTENT)
