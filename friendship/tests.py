from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import status
from .views import accept_friend_request

from .models import FriendRequest, Friend
from .serializers import UserSerializer, FriendRequestIdSerializer

class FriendRequestModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        self.request = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)

    def test_accept(self):
        self.request.accept()
        self.assertEqual(self.request.status, FriendRequest.ACCEPTED)

    def test_decline(self):
        self.request.decline()
        self.assertEqual(self.request.status, FriendRequest.DECLINED)

class FriendModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        self.friendship = Friend.objects.create(user=self.user1, friend=self.user2)

    def test_make_friends(self):
        user3 = User.objects.create_user(username='user3', password='12345')
        Friend.make_friends(self.user1, user3)
        self.assertTrue(Friend.objects.filter(user=self.user1, friend=user3).exists())


class RegisterViewTestCase(APITestCase):

    def test_valid_registration(self):
        url = reverse('register')
        data = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_registration(self):
        url = reverse('register')
        data = {
            "username": "",
            "password": "testuser"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_invalid_username_format(self):
        url = reverse('register')
        data = {
            "username": "te***",
            "password": "testpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_short_password(self):
        url = reverse('register')
        data = {
            "username": "testuser",
            "password": ""
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class SendFriendRequestViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='password2'
        )
        self.client.force_authenticate(self.user1)

    def test_send_friend_request_to_nonexistent_user(self):
        response = self.client.post(
            reverse('send_friend_request'),
            data={'to_user': 99999},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'Пользователь не найден.'})

    def test_send_friend_request_from_unauthenticated_user(self):
        self.client.logout()
        response = self.client.post(
            reverse('send_friend_request'),
            data={'to_user': self.user2.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_send_friend_request_successfully(self):
        response = self.client.post(
            reverse('send_friend_request'),
            data={'to_user': self.user2.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_send_friend_request_to_self(self):
        response = self.client.post(
            reverse('send_friend_request'),
            data={'to_user': self.user1.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_friend_request_to_user_with_existing_active_request(self):
        FriendRequest.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status=FriendRequest.PENDING
        )
        response = self.client.post(
            reverse('send_friend_request'),
            data={'to_user': self.user2.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AcceptFriendRequestViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpassword'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpassword'
        )
        self.friend_request = FriendRequest.objects.create(
            from_user=self.user1,
            to_user=self.user2
        )
        self.url = reverse('accept_friend_request')

    def test_accept_friend_request_successfully(self):
        self.client.force_authenticate(user=self.user2)
        data = {'friend_request_id': self.friend_request.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': f"Пользователь {self.user1.username} добавлен в друзья"})
        self.assertTrue(Friend.objects.filter(user=self.user1, friend=self.user2).exists())
        self.assertFalse(FriendRequest.objects.filter(id=self.friend_request.id).exists())

    def test_accept_nonexistent_friend_request(self):
        self.client.force_authenticate(user=self.user2)
        data = {'friend_request_id': 999}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': 'Запрос в друзья не найден'})

    def test_accept_friend_request_by_nonrecipient_user(self):
        self.client.force_authenticate(user=self.user1)
        data = {'friend_request_id': self.friend_request.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'message': 'Вы не можете удовлетворить эту заявку в друзья'})

    def test_accept_friend_request_by_unauthenticated_user(self):
        data = {'friend_request_id': self.friend_request.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FriendsViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='password')
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_friends(self):
        friend = Friend.objects.create(user=self.user1, friend=self.user2)
        url = '/api/friends/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_response_data = [{'id': friend.id, 'friend': 'user2'}]
        self.assertEqual(len(response.data), 1)
    
    def test_friends_no_friends(self):
        url = '/api/friends/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_response_data = {"Статус": "Нет друзей"}
        self.assertEqual(response.data, expected_response_data)


class RemoveFriendViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        self.user3 = User.objects.create_user(username='user3', password='12345')
        Friend.objects.create(user=self.user1, friend=self.user2)
        Friend.objects.create(user=self.user2, friend=self.user1)
        Friend.objects.create(user=self.user2, friend=self.user3)
        Friend.objects.create(user=self.user3, friend=self.user2)

    def test_remove_friend_successfully(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse('remove_friend', kwargs={'user_id': self.user2.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'Статус': f'Пользователь {self.user2.username} удален из друзей'})
        self.assertEqual(Friend.objects.count(), 2)

    def test_remove_friend_user_not_found(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse('remove_friend', kwargs={'user_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'Пользователь не найден.'})
        self.assertEqual(Friend.objects.count(), 4)

    def test_remove_friend_not_a_friend(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse('remove_friend', kwargs={'user_id': self.user3.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'Статус': 'Данный пользователь не является вашим другом.'})
        self.assertEqual(Friend.objects.count(), 4)
