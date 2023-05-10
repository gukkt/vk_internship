from enum import Enum

from django.db import models

from user.models import User


class Friendship(models.Model):
    """Модель для хранения дружеских отношений."""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')

    class Meta:
        verbose_name = 'Friends'

    def __str__(self):
        return f'{self.user1} - {self.user2}'


class FriendRequests(models.Model):
    """Модель для хранения запросов на дружбу между пользователями."""

    class RequestStatus(Enum):
        """Перечисление для описания всех возможных состояний отношения между двумя пользователями."""
        EMPTY = "There is nothing"
        OUTGOING_REQUEST = "Outgoing request"
        INCOMING_REQUEST = "Incoming request"
        ALREADY_FRIENDS = "Already friends"

    request_from = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='request_from', verbose_name='Friendship request from'
    )
    request_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='request_to', verbose_name='Friendship request for'
    )

    class Meta:
        verbose_name = 'Friend requests'
        unique_together = (('request_from', 'request_to'), ('request_to', 'request_from'))
