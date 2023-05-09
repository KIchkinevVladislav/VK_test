from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Friend, FriendRequest


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""
    class Meta:
        model = User
        fields = '__all__'


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']


    def create(self, validated_data):
        """Создание нового запроса на добавление в друзья в базе данных"""
        from_user = self.context.get('request').user
        to_user = validated_data.get('to_user')
        return FriendRequest.objects.create(from_user=from_user, to_user=to_user)


class FriendSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Friend"""
    user = UserSerializer(read_only=True)
    friend = UserSerializer(read_only=True)
    
    class Meta:
        model = Friend
        fields = ('id', 'user', 'friend')

    def to_representation(self, instance):
        """Функция возвращет никнеймы пользователя и друга"""
        representation = super().to_representation(instance)
        representation['user'] = representation['user']['username']
        representation['friend'] = representation['friend']['username']
        return representation
