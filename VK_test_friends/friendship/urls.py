from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'), # регистрация нового пользователя
    path('friend-request/', views.send_friend_request, name='send_friend_request'), # отправка заявки в друзья
    path('friend-request/accept/', views.accept_friend_request, name='accept_friend_request'), #+проверяем что заявка существует и что заявка на наше имя, удаляет
    path('friend-request/decline/', views.decline_friend_request, name='decline_friend_request'), #+ проверяем что заявка существует и что заявка на наше имя, удаляет
    path('friend-requests/', views.friend_requests, name='friend_requests'), # возвращает с именами и датами +
    path('friends/', views.friends, name='friends'), #возвращает список друзей с указанием никнеймов и id +
    path('friend-status/<int:user_id>/', views.friend_status, name='friend_status'), # все верно возвращает +
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'), # удаляет из обоих моделей +
]
