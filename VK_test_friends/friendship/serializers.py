from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Friend, FriendRequest


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""
    class Meta:
        model = User
        fields = '__all__'


# class FriendRequestSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели FriendRequest"""
#     from_user = serializers.HiddenField(default=serializers.CurrentUserDefault())

#     class Meta:
#         model = FriendRequest
#         fields = ('id', 'from_user', 'to_user') до патча с запросами

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.CharField(source='from_user.username')
    to_user = serializers.CharField(source='to_user.username')

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']



class FriendSerializer(serializers.ManyRelatedField):
    """Сериализатор для модели Friend"""
    user = UserSerializer(read_only=True)
    friend = UserSerializer(read_only=True)
    
    class Meta:
        model = Friend
        fields = ('id', 'user', 'friend')
