from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.models import User
from user.serializers import UserSerializer


@extend_schema(
    summary='Получение пользователя по id',
    methods=['GET'],
    responses={
        status.HTTP_200_OK: UserSerializer,
        status.HTTP_404_NOT_FOUND: str
    },
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='ID пользователя',
            required=True,
            type=int,
        )
    ]
)
@api_view(['GET'])
def user_detail(request, user_id: int):
    """Получение пользователя по id"""
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary='Создание пользователя',
    methods=['POST'],
    responses={
        status.HTTP_201_CREATED: UserSerializer,
        status.HTTP_400_BAD_REQUEST: str,
    },
)
@api_view(['POST'])
def user_create(request):
    """Создание пользователя"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)
