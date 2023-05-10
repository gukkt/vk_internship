from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from friendship.models import Friendship, FriendRequests
from friendship.services import send_request, accept_request, decline_request, cancel_request, is_friends, \
    request_exists, get_incoming_requests, get_outgoing_requests, get_user_friends
from user.models import User
from user.serializers import UserSerializer


@extend_schema(
    summary='Отображение списка друзей пользователя',
    methods=['GET'],
    responses={
        status.HTTP_200_OK: dict,
    },
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='ID пользователя',
            required=True,
            type=int,
            location='path',
        ),
    ],
    examples=[
        OpenApiExample(
            name='Отображение списка друзей пользователя',
            value={
                'friends': [
                    {
                        'id': 1,
                        'username': 'Иван',
                    },
                    {
                        'id': 2,
                        'username': 'Кирилл',
                    },
                ],
            },
            status_codes=['200'],
        ),
    ],
)
class FriendshipsListView(ListAPIView):
    """Отображение списка друзей пользователя"""
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        friends = get_user_friends(user_id)
        serializer = self.get_serializer(friends, many=True)
        return Response({'friends': serializer.data})


@extend_schema(
    summary='Отображение списка входящих/исходящих запросов на дружбу',
    methods=['GET'],
    responses={
        status.HTTP_200_OK: dict,
        status.HTTP_400_BAD_REQUEST: str,
    },
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='ID пользователя',
            required=True,
            type=int,
            location='path',
        ),
        OpenApiParameter(
            name='requests_type',
            description='Тип запросов (incoming/outgoing)',
            required=True,
            type=str,
            location='path',
        ),
    ],
    examples=[
        OpenApiExample(
            name='Отображение списка входящих запросов на дружбу',
            value={
                'requests_users': [
                    {
                        'id': 1,
                        'username': 'Иван',
                    },
                    {
                        'id': 2,
                        'username': 'Кирилл',
                    },
                ],
                'requests_type': 'incoming',
                'count': 2,
            },
            status_codes=['200'],
        ),
        OpenApiExample(
            name='Отображение списка исходящих запросов на дружбу',
            value={
                'requests_users': [
                    {
                        'id': 1,
                        'username': 'Иван',
                    },
                ],
                'requests_type': 'outgoing',
                'count': 1,
            },
            status_codes=['200'],
        ),
        OpenApiExample(
            name='Отображение списка входящих запросов на дружбу (ошибка: указан неверный тип запросов)',
            value='action must be "incoming" or "outgoing"',
            status_codes=['400'],
        ),
    ],

)
class FriendshipRequestsListView(ListAPIView):
    """Отображение списка входящих/исходящих запросов на дружбу"""
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        action = self.kwargs.get('requests_type')
        if action is None:
            raise ValidationError('action must be specified')
        match action:
            case 'incoming':
                users = get_incoming_requests(user_id)
            case 'outgoing':
                users = get_outgoing_requests(user_id)
            case _:
                raise ValidationError('action must be "incoming" or "outgoing"')

        return User.objects.filter(id__in=users)

    def list(self, request, *args, **kwargs):
        action = self.kwargs.get('requests_type').lower()
        data = UserSerializer(self.get_queryset(), many=True).data
        return Response({"requests_users": data, "requests_type": action, "count": len(data)})


@extend_schema(
    summary='Отправка/принятие/отклонение/отмена запроса на дружбу',
    methods=['POST'],
    responses={
        status.HTTP_200_OK: dict,
        status.HTTP_400_BAD_REQUEST: str,
    },
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='ID пользователя',
            required=True,
            type=int,
            location='path',
        ),
        OpenApiParameter(
            name='target_user_id',
            description='ID пользователя, которому отправляется запрос',
            required=True,
            type=int,
            location='path',
        ),
        OpenApiParameter(
            name='action',
            description='Тип действия (send_request/accept_request/decline_request/cancel_request)',
            required=True,
            type=str,
            location='path',
        ),
    ],
    examples=[
        OpenApiExample(
            name='Отправка запроса на дружбу',
            value={
                'message': 'Запрос на дружбу отправлен',
            },
            status_codes=['200'],
        ),
        OpenApiExample(
            name='Принятие запроса на дружбу',
            value={
                'message': 'Запрос на дружбу принят',
            },
            status_codes=['200'],
        ),
        OpenApiExample(
            name='Отклонение запроса на дружбу',
            value={
                'message': 'Запрос на дружбу отклонен',
            },
            status_codes=['200'],
        ),
        OpenApiExample(
            name='Отмена запроса на дружбу',
            value={
                'message': 'Запрос на дружбу отменен',
            },
            status_codes=['200'],
        ),
        OpenApiExample(
            name='Отправка запроса на дружбу (ошибка: user_id равен target_user_id)',
            value='user_id must not be equal to target_user_id',
            status_codes=['400'],
        ),
        OpenApiExample(
            name='Отправка запроса на дружбу (ошибка: указан неверный тип действия)',
            value='unknown action "unknown_action" (must be one of: send_request, accept_request, decline_request, cancel_request)',
            status_codes=['400'],
        ),
    ],
)
class FriendshipRequestsView(APIView):
    """Отправка/принятие/отклонение/отмена запроса на дружбу"""
    def post(self, request, user_id: int, target_user_id: int, action: str) -> Response:
        if user_id == target_user_id:
            raise ValidationError('user_id must not be equal to target_user_id')

        match action.lower():
            case 'send_request':
                return send_request(user_id, target_user_id)
            case 'accept_request':
                return accept_request(user_id, target_user_id)
            case 'decline_request':
                return decline_request(user_id, target_user_id)
            case 'cancel_request':
                return cancel_request(user_id, target_user_id)
            case _:
                raise ValidationError(f'unknown action "{action}" '
                                      f'(must be one of: send_request, accept_request, decline_request, cancel_request)')


@extend_schema(
    summary='Удаление друга из списка друзей',
    methods=['POST'],
    responses={
        status.HTTP_200_OK: dict,
        status.HTTP_400_BAD_REQUEST: str,
    },
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='ID пользователя',
            required=True,
            type=int,
            location='path',
        ),
        OpenApiParameter(
            name='target_user_id',
            description='ID пользователя, которого нужно удалить из списка друзей',
            required=True,
            type=int,
            location='path',
        ),
    ],
    examples=[
        OpenApiExample(
            name='Удаление друга из списка друзей',
            value={
                'status': 'Friend deleted',
            },
            status_codes=['200'],
        ),
        OpenApiExample(
            name='Удаление друга из списка друзей (ошибка: пользователи не являются друзьями)',
            value='users are not friends',
            status_codes=['400'],
        ),
        OpenApiExample(
            name='Удаление друга из списка друзей (ошибка: user_id равен target_user_id)',
            value='user_id must not be equal to target_user_id',
            status_codes=['400'],
        ),
    ],
)
class DeleteFriendView(APIView):
    """Удаление друга из списка друзей"""
    def post(self, request, user_id: int, target_user_id: int) -> Response:
        if user_id == target_user_id:
            raise ValidationError('user_id must not be equal to target_user_id')

        if not is_friends(user_id, target_user_id):
            raise ValidationError('users are not friends')
        Friendship.objects.filter(Q(user1=user_id, user2=target_user_id) | Q(user1=target_user_id, user2=user_id)).delete()
        return Response({'status': 'Friend deleted'})


@extend_schema(
    summary='Проверка статуса дружбы для пользователя status_for к пользователю status_with',
    methods=['GET'],
    responses={
        status.HTTP_200_OK: dict,
        status.HTTP_400_BAD_REQUEST: str,
    },
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='ID пользователя, для которого нужно проверить статус дружбы',
            required=True,
            type=int,
            location='path',
        ),
        OpenApiParameter(
            name='target_user_id',
            description='ID пользователя, к которому нужно проверить статус дружбы',
            required=True,
            type=int,
            location='path',
        ),
    ],
    examples=[
        OpenApiExample(
            name='Проверка статуса дружбы для пользователя status_for к пользователю status_with',
            value={
                'status': 'Already friends',
                'message': 'Пользователи уже являются друзьями',
            },
            status_codes=['200'],
        ),
        OpenApiExample(
            name='Проверка статуса дружбы для пользователя status_for к пользователю status_with',
            value={
                'status': 'Outgoing request',
                'message': 'У пользователя status_for есть исходящий запрос к пользователю status_with',
            },
            status_codes=['200'],
        ),
        OpenApiExample(
            name='Проверка статуса дружбы для пользователя status_for к пользователю status_with',
            value={
                'status': 'Incoming request',
                'message': 'У пользователя status_with есть входящий запрос от пользователя status_for',
            },
            status_codes=['200'],
        ),
        OpenApiExample(
            name='Проверка статуса дружбы для пользователя status_for к пользователю status_with (ошибка: user_id равен target_user_id)',
            value='user_id must not be equal to target_user_id',
            status_codes=['400'],
        ),
    ],
)
class FriendshipStatusView(APIView):
    def get(self, request, user_id: int, target_user_id: int):
        """Проверка статуса дружбы для пользователя status_for к пользователю status_with"""
        # Проверка на то, являются ли они друзьями
        if is_friends(user_id, target_user_id):
            return Response({
                'status': FriendRequests.RequestStatus.ALREADY_FRIENDS.name,
                'message': FriendRequests.RequestStatus.ALREADY_FRIENDS.value,
            })

        # Проверка на наличие исходящего запроса от status_for для status_with
        if request_exists(request_from=user_id, request_to=target_user_id):
            return Response({
                'status': FriendRequests.RequestStatus.OUTGOING_REQUEST.name,
                'message': FriendRequests.RequestStatus.OUTGOING_REQUEST.value,
            })

        # Проверка на наличие входящего запроса для status_for от status_with
        if request_exists(request_from=user_id, request_to=target_user_id):
            return Response({
                'status': FriendRequests.RequestStatus.INCOMING_REQUEST.name,
                'message': FriendRequests.RequestStatus.INCOMING_REQUEST.value,
            })

        return Response({
            'status': FriendRequests.RequestStatus.EMPTY.name,
            'message': FriendRequests.RequestStatus.EMPTY.value,
        })
