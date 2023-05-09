from django.contrib.auth.models import User
from django.db import models

# используем базовую модель пользователя в Django

class FriendRequest(models.Model):
    """Модель хранит статус запросов пользователей"""
    PENDING = 'P'
    ACCEPTED = 'A'
    DECLINED = 'D'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined')
    )

    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def accept(self):
        self.status = self.ACCEPTED
        self.save()

    def decline(self):
        self.status = self.DECLINED
        self.save()


class Friend(models.Model):
    """Модель хранит связки пользователей как друзей"""
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='my_friends', on_delete=models.CASCADE)


    class Meta:
        unique_together = ('user', 'friend') # уникальная связка пользователя с другом


    @classmethod
    def make_friends(cls, user1, user2):
        """Метод для добавления пользователей в друзья"""
        friend1, created = cls.objects.get_or_create(user=user1, friend=user2)
        friend2, created = cls.objects.get_or_create(user=user2, friend=user1)
        
        