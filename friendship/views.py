from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UserSerializer, FriendRequestSerializer, FriendSerializer, FriendRequestIdSerializer
from django.contrib.auth.models import User
from .models import Friend, FriendRequest


@extend_schema(
    tags=['Posts'],
    request=UserSerializer,
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Регистрация пользователя"""
    # отправляется JSON-объект формата: {"username": "test", "password": "testpassword"}
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Posts'],
    request=FriendRequestSerializer,
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_friend_request(request):
    """Отправка запроса на добавление в друзья"""
    # отправляется JSON-объект формата: {"to_user": id}, где id - целое число, индентификатор пользователя, к которому направляется запрос
    from_user = request.user 
    to_user_id = request.data.get('to_user')
    try:
    # проверяем, что запрашиваемый пользователь существует
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Пользователь не найден.'}, 
            status=status.HTTP_404_NOT_FOUND
            )
    if from_user.id == to_user_id:
    # проверяем, что запрашиваемый пользователь не тот, кто запрашивает
        return Response(
            {'detail': 'Вы не можете отправить запрос самому себе.'}, 
            status=status.HTTP_400_BAD_REQUEST
            )
    existing_request = FriendRequest.objects.filter(
        from_user=from_user, 
        to_user=to_user, 
        status=FriendRequest.PENDING).first()
    # проверяем, что нет такой же активной заявки в друзья
    if existing_request:
        return Response(
            {'detail': 'У вас уже есть активная заявка на добавление в друзья для этого пользователя.'}, 
            status=status.HTTP_400_BAD_REQUEST
            )
    
    data = request.data.copy()
    data['from_user'] = from_user.pk
    serializer = FriendRequestSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()

        # Проверяем, есть ли заявка от to_user к from_user, для автоматического одобрения двух заявок и создание моделей дружбы
        friend_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user).first()
        if friend_request:
            # Создаем объект Friend для обоих пользователей
            Friend.make_friends(from_user, to_user)
            # Удаляем соответствующие заявки
            friend_request_2 = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).first()
            if friend_request_2:
                friend_request_2.delete()
            friend_request.delete()
            message = f"Пользователь {to_user.username} добавлен в друзья"
            return Response({"message": message}, status=status.HTTP_200_OK)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Posts'],
    request=FriendRequestIdSerializer,
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_friend_request(request):
    """Добавление пользователя в друзья по номеру заявки"""
    # отправляется JSON-объект формата: {"friend_request_id": 1}, где число - номер заявки
    try:
        # проверяем, что запрос существует
        friend_request = FriendRequest.objects.get(id=request.data['friend_request_id'])
    except FriendRequest.DoesNotExist:
        return Response(
            {"message": "Запрос в друзья не найден"}, 
            status=status.HTTP_404_NOT_FOUND
            )
    if friend_request.to_user != request.user:
        # проверяем, что к текущему пользователю
        return Response(
            {"message": "Вы не можете удовлетворить эту заявку в друзья"}, 
            status=status.HTTP_400_BAD_REQUEST
            )
    friend_request.accept()
    to_user = friend_request.from_user
    from_user = friend_request.to_user
    Friend.make_friends(from_user, to_user)
    message = f"Пользователь {to_user.username} добавлен в друзья"
    friend_request.delete()
    return Response({"message": message}, status=status.HTTP_200_OK)


@extend_schema(tags=['Posts'],
    request=FriendRequestIdSerializer,
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def decline_friend_request(request):
    """Отказ в добавлении в друзья по номеру заявки"""
    # отправляется JSON-объект формата: {"friend_request_id": 1}, где число - номер заявки
    try:
        # проверяем, что запрос существует
        friend_request = FriendRequest.objects.get(id=request.data['friend_request_id'])
    except FriendRequest.DoesNotExist:
        return Response(
            {"message": "Запрос в друзья не найден"}, 
            status=status.HTTP_404_NOT_FOUND
            )
    if friend_request.to_user != request.user:
        # проверяем, что запрос к текущему пользователю
        return Response(
            {"message": "Вы не можете отклонить эту заявку в друзья"}, 
            status=status.HTTP_400_BAD_REQUEST
            )
    from_user = friend_request.from_user
    friend_request.decline()
    message = f"Запрос на добавление в друзья от пользователя {from_user.username} отклонен"
    friend_request.delete()
    return Response({"message": message}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def friend_requests(request):
    """Возвращает список входящих и исходящих заявок в друзья"""
    user = request.user
    incoming_requests = FriendRequest.objects.filter(to_user=user)
    outgoing_requests = FriendRequest.objects.filter(from_user=user)
    incoming_serializer = FriendRequestSerializer(incoming_requests, many=True)
    outgoing_serializer = FriendRequestSerializer(outgoing_requests, many=True)
    return Response({'Входящие заявки': incoming_serializer.data, 'Исходящие заявки': outgoing_serializer.data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def friends(request):
    """Посмотреть список друзей"""
    user = request.user
    friends = Friend.objects.filter(user=user)
    if not friends:
        return Response({"Статус": "Нет друзей"})
    serializer = FriendSerializer(friends, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def friend_status(request, user_id):
    """
    Возвращает статус запрашиваемого пользователями или наличие заявок
    :param user_id:
    """
    user = request.user
    if user.id == user_id:
        return Response({'Статус': 'Вы указали свой id'})
    try:
    # проверяем, что запрашиваемый пользователь существует
        to_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Пользователь не найден.'}, 
            status=status.HTTP_404_NOT_FOUND
            )
    try:
        # проверяем, являются ли пользователи друзьями
        friend = Friend.objects.get(user=user, friend__id=user_id)
        friend_status = 'Вы друзья'
    except Friend.DoesNotExist:
        try:
            # проверяем имеется ли исходящий запрос
            FriendRequest.objects.get(from_user=user, to_user__id=user_id, status=FriendRequest.PENDING)
            friend_status = 'Вы отправляли запрос на добавление в друзья'
        except FriendRequest.DoesNotExist:
            try:
                # проверяем имеется ли входящий запрос
                FriendRequest.objects.get(from_user__id=user_id, to_user=user, status=FriendRequest.PENDING)
                friend_status = 'Имеется запрос на добавление в друзья от этого пользователя'
            except FriendRequest.DoesNotExist:
                    # итоговое исключение
                    friend_status = 'Не друзья'
    
    return Response({'Статус': friend_status})


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_friend(request, user_id):
    """
    Удалить друга, статус дружбы также удаляется у другого пользователя
    :param user_id:
    """
    user = request.user
    if user.id == user_id:
        return Response({'Статус': 'Вы указали свой id'})
    try:
    # проверяем, что запрашиваемый пользователь существует
        to_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Пользователь не найден.'}, 
            status=status.HTTP_404_NOT_FOUND
            )
    friend = Friend.objects.filter(user=user, friend__id=user_id).first()
    if not friend:
        return Response(
            {'Статус': 'Данный пользователь не является вашим другом.'}, 
            status=status.HTTP_400_BAD_REQUEST
            )
    friend_name = friend.friend.username
    friend.delete()
    # Удаляем запись из модели Friend у другого пользователя
    opposite_friend = Friend.objects.filter(user=friend.friend, friend=user).first()
    if opposite_friend:
        opposite_friend.delete()
    return Response({'Статус': f'Пользователь {friend_name} удален из друзей'})
