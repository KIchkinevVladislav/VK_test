from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'), #+
    path('friend-request/', views.send_friend_request, name='send_friend_request'), #+ должна ли удаляться заявка? когда принятие или отклонение
    path('friend-request/accept/', views.accept_friend_request, name='accept_friend_request'), #+проверяем что заявка существует и что заявка на наше имя, что не отклонена
    path('friend-request/decline/', views.decline_friend_request, name='decline_friend_request'), #+ проверяем что заявка существует и что заявка на наше имя, что о
    path('friend-requests/', views.friend_requests, name='friend_requests'), # возвращает с именами и датами
    path('friends/', views.friends, name='friends'),
    path('friend-status/<int:user_id>/', views.friend_status, name='friend_status'), # все верно возвращает
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('automatic-friend-request/<int:user_id>/', views.send_automatic_friend_request, name='send_automatic_friend_request'),
]
