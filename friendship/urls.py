from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'), 
    # регистрация нового пользователя
    path('friend-request/', views.send_friend_request, name='send_friend_request'), 
    # отправка заявки в друзья
    path('friend-request/accept/', views.accept_friend_request, name='accept_friend_request'), 
    # одобрение заявки
    path('friend-request/decline/', views.decline_friend_request, name='decline_friend_request'), 
    # отказ в заявке
    path('friend-requests/', views.friend_requests, name='friend_requests'), 
    # запрос наличия поступивших и отправленных заявок
    path('friends/', views.friends, name='friends'), 
    # запрос списка друзей
    path('friend-status/<int:user_id>/', views.friend_status, name='friend_status'), 
    # узнать является ли пользователь другом и имеются ли заявки
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'), 
    # удаление из друзей
]
