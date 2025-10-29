import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Diary

User = get_user_model()


class TestUserAuthentication(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.register_url = '/api/users/register/'
        self.login_url = '/api/users/login/'
        self.logout_url = '/api/users/logout/'
        self.delete_url = '/api/users/delete/'
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'password2': 'TestPass123'
        }
        
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='TestPass123'
        )

    def test_user_registration_success(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Вы успешно зарегистрировались!')
        
        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)

    def test_user_registration_duplicate_username(self):
        """Тест регистрации с существующим username"""
        data = self.user_data.copy()
        data['username'] = 'existinguser'
        data['email'] = 'new@example.com'
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями"""
        data = self.user_data.copy()
        data['password2'] = 'DifferentPass123'
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        """Тест успешного входа"""
        login_data = {
            'email': 'existing@example.com',
            'password': 'TestPass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

    def test_user_login_wrong_password(self):
        """Тест входа с неверным паролем"""
        login_data = {
            'email': 'existing@example.com',
            'password': 'WrongPassword'
        }
        
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_inactive_account(self):
        """Тест входа с неактивным аккаунтом"""
        self.user.is_active = False
        self.user.save()
        
        login_data = {
            'email': 'existing@example.com',
            'password': 'TestPass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_success(self):
        """Тест успешного выхода"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        logout_data = {'refresh': str(refresh)}
        response = self.client.post(self.logout_url, logout_data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_missing_token(self):
        """Тест выхода без refresh токена"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_soft_delete_account(self):
        """Тест мягкого удаления аккаунта"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.delete(self.delete_url, {'refresh': str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class TestUserProfile(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile_url = '/api/users/update/'
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123',
            first_name='Old',
            last_name='Name'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_update_profile_success(self):
        """Тест успешного обновления профиля"""
        update_data = {
            'first_name': 'New',
            'last_name': 'Name'
        }
        
        response = self.client.patch(self.profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'New')

    def test_update_profile_duplicate_email(self):
        """Тест обновления профиля с существующим email"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123'
        )
        
        update_data = {'email': 'other@example.com'}
        response = self.client.patch(self.profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_unauthorized(self):
        """Тест обновления профиля без авторизации"""
        client = APIClient()
        response = client.patch(self.profile_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestDiaryPermissions(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='TestPass123'
        )
        
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='TestPass123'
        )
        
        self.diary = Diary.objects.create(
            owner=self.owner,
            title='Test Diary'
        )
        
        # Правильный URL для дневника
        self.diary_url = f'/api/diary/{self.diary.id}/'

    def test_get_diary_owner_success(self):
        """Тест доступа владельца к своему дневнику"""
        refresh = RefreshToken.for_user(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(self.diary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Diary')

    def test_get_diary_other_user_forbidden(self):
        """Тест запрета доступа другого пользователя к чужому дневнику"""
        refresh = RefreshToken.for_user(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(self.diary_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_diary_unauthorized(self):
        """Тест доступа без авторизации"""
        response = self.client.get(self.diary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_nonexistent_diary(self):
        """Тест запроса несуществующего дневника"""
        refresh = RefreshToken.for_user(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = '/api/diary/999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_diary_inactive_user(self):
        """Тест доступа неактивного пользователя"""
        self.owner.is_active = False
        self.owner.save()
        
        refresh = RefreshToken.for_user(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(self.diary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestModels(APITestCase):
    def test_user_soft_delete(self):
        """Тест мягкого удаления пользователя"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        
        self.assertTrue(user.is_active)
        user.soft_delete()
        self.assertFalse(user.is_active)

    def test_user_is_deleted(self):
        """Тест метода is_deleted"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        
        self.assertFalse(user.is_deleted())
        user.soft_delete()
        self.assertTrue(user.is_deleted())

    def test_diary_creation(self):
        """Тест создания дневника"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        
        diary = Diary.objects.create(
            owner=user,
            title='Test Diary'
        )
        
        self.assertEqual(diary.owner, user)
        self.assertEqual(diary.title, 'Test Diary')


class TestServices(APITestCase):
    def test_user_auth_service_register_success(self):
        """Тест сервиса регистрации пользователя"""
        from .services import UserAuthService
        
        user_data = {
            'username': 'serviceuser',
            'email': 'service@example.com',
            'password': 'TestPass123'
        }
        
        user, error = UserAuthService.register_user(user_data)
        self.assertIsNotNone(user)
        self.assertIsNone(error)
        self.assertEqual(user.username, 'serviceuser')

    def test_user_auth_service_register_duplicate(self):
        """Тест сервиса регистрации с дубликатом"""
        from .services import UserAuthService
        
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='TestPass123'
        )
        
        user_data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'TestPass123'
        }
        
        user, error = UserAuthService.register_user(user_data)
        self.assertIsNone(user)
        self.assertIsNotNone(error)

    def test_user_auth_service_login(self):
        """Тест сервиса входа пользователя"""
        from .services import UserAuthService
        
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        
        validated_data = {'user': user, 'email': 'test@example.com'}
        response = UserAuthService.login_user(validated_data)
        
        self.assertIn('tokens', response)
        self.assertIn('access', response['tokens'])