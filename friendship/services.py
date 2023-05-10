from django.db.models import Q, When, Case, F, IntegerField
from rest_framework import status
from rest_framework.response import Response

from friendship.models import FriendRequests, Friendship
from user.models import User


def send_request(user_id: int, target_user_id: int) -> Response:
    """Создание запроса на дружбу"""
    try:
        user = User.objects.get(id=user_id)
        target_user = User.objects.get(id=target_user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Если уже являются друзьями
    if is_friends(user1=user_id, user2=target_user_id):
        return Response(
            {
                "success": False,
                "message": "This user is already your friend",
            },
            status=status.HTTP_409_CONFLICT,
        )

    # Такой запрос уже существует
    if request_exists(user_id, target_user_id):
        return Response(
            {
                "success": False,
                "message": "You already have such a request",
            },
            status=status.HTTP_409_CONFLICT,
        )

    # Перекрёстные запросы
    if request_exists(target_user_id, user_id):
        Friendship.objects.create(user1=user, user2=target_user)
        return Response(
            {
                "success": True,
                "message": "You have successfully sent the request. "
                           "Since you already have a request from this user, you automatically become friends.",
            },
            status=status.HTTP_201_CREATED,
        )

    # Все условия проверены, создаём новый запрос
    FriendRequests.objects.create(request_from=user, request_to=target_user)
    return Response(
        {
            "success": True,
            "message": "You have successfully sent the request."
        },
        status=status.HTTP_201_CREATED,
    )


def cancel_request(user_id: int, target_user_id: int) -> Response:
    """Пользователь передумал и решил отменить свою заявку в друзья"""
    if FriendRequests.objects.filter(request_from=user_id, request_to=target_user_id).delete()[0]:
        return Response(
            {
                "success": True,
                "message": "You have successfully canceled the request."
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {
            "success": False,
            "message": "You don't have such a request."
        },
        status=status.HTTP_404_NOT_FOUND,
    )


def accept_request(user_id: int, target_user_id: int) -> Response:
    """user_id принимает запрос дружбы от target_user_id"""
    user1 = User.objects.get(id=user_id)
    user2 = User.objects.get(id=target_user_id)
    if request_exists(target_user_id, user_id):
        Friendship.objects.create(user1=user1, user2=user2)
        FriendRequests.objects.filter(request_from=target_user_id, request_to=user_id).delete()
        return Response(
            {
                "success": True,
                "message": "You have successfully accepted the request."
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {
            "success": False,
            "message": "You don't have such a request."
        },
        status=status.HTTP_404_NOT_FOUND,
    )


def decline_request(user_id: int, target_user_id: int) -> Response:
    """user_id отклоняет запрос дружбы от target_user_id"""
    if FriendRequests.objects.filter(request_from=target_user_id, request_to=user_id).delete()[0]:
        return Response(
            {
                "success": True,
                "message": "You have successfully declined the request."
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {
            "success": False,
            "message": "You don't have such a request."
        },
        status=status.HTTP_404_NOT_FOUND,
    )


def request_exists(request_from: int, request_to: int) -> bool:
    return FriendRequests.objects.filter(request_from=request_from, request_to=request_to).exists()


def is_friends(user1: int, user2: int) -> bool:
    return Friendship.objects.filter(Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)).exists()


def get_incoming_requests(user_id: int):
    """Получение входящих запросов в друзья"""
    return FriendRequests.objects.filter(request_to=user_id).values_list("request_from", flat=True)


def get_outgoing_requests(user_id: int):
    """Получение исходящих запросов в друзья"""
    return FriendRequests.objects.filter(request_from=user_id).values_list("request_to", flat=True)


def get_user_friends(user_id: int):
    friends = Friendship.objects \
        .filter(Q(user1__id=user_id) | Q(user2__id=user_id)) \
        .annotate(
            friend_id=Case(
                When(user1=user_id, then=F('user2')),
                When(user2=user_id, then=F('user1')),
                output_field=IntegerField(),
          )
        ) \
        .values_list('friend_id', flat=True)
    return User.objects.filter(id__in=friends)
