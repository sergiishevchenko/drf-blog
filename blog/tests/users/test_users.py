from unittest.mock import MagicMock, patch

import jwt
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.services import create_user


pytestmark = pytest.mark.django_db


@pytest.fixture()
def user():
    return create_user(
        email='serg@email.com',
        first_name='Mark',
        last_name='Twain',
        password='password',
    )


@pytest.fixture()
def active_user():
    user = User.objects.create_user(
        email='serg@email.com',
        first_name='Mark',
        last_name='Twain',
        password='password',
    )

    user.is_verified = True
    user.save()
    return user


class TestCreateUser:
    register_url = reverse('users:api-v1:register-user')

    def test_create_user(self, api_client):
        response = api_client.post(
            f'{self.register_url}',
            data={
                'email': 'serg@email.com',
                'first_name': 'Mark',
                'last_name': 'Twain',
                'password': 'password',
                'confirm_password': 'password',
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


class TestUserActivation:
    def test_verify_user(self, api_client, user):
        token = RefreshToken.for_user(user).access_token

        user_id = user.id
        mocked_jwt_decode = MagicMock(return_value={'user_id': user_id})

        with patch('jwt.decode', mocked_jwt_decode):
            url = reverse('users:api-v1:verify-user', kwargs={'token': token})
            response = api_client.get(url)

            user.refresh_from_db()

            assert response.status_code == status.HTTP_200_OK
            assert (response.data['detail'] == 'Thank you for your email confirmation. Now you can login your account.')
            assert user.is_verified is True

    def test_user_already_verified(self, api_client, user):
        user.is_verified = True
        user.save()
        token = RefreshToken.for_user(user).access_token

        user_id = user.id
        mocked_jwt_decode = MagicMock(return_value={'user_id': user_id})
        with patch('jwt.decode', mocked_jwt_decode):
            url = reverse('users:api-v1:verify-user', kwargs={'token': token})
            response = api_client.get(url)

            user.refresh_from_db()

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data['detail'] == 'Your account is already verified.'

    def test_token_is_expired(self, api_client, user):
        token = RefreshToken.for_user(user).access_token

        with patch('jwt.decode', side_effect=jwt.ExpiredSignatureError):
            url = reverse('users:api-v1:verify-user', kwargs={'token': token})
            response = api_client.get(url)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data['detail'] == 'Activation link is expired'


class TestJwtToken:
    url = reverse('users:api-v1:jwt-create')

    def test_create_jwt_token(self, api_client, active_user):
        response = api_client.post(
            f'{self.url}', data={'email': 'serg@email.com', 'password': 'password'}
        )

        access_token = response.data['access']
        refresh_token = response.data['refresh']

        assert access_token is not None
        assert refresh_token is not None

    def test_refresh_jwt_token(self, api_client, active_user):
        response = api_client.post(
            f'{self.url}', data={'email': 'serg@email.com', 'password': 'password'}
        )

        access_token = response.data['access']

        body = {'refresh': response.data['refresh']}
        headers = {'Authorization': f'Bearer {access_token}'}

        response = api_client.post(
            path=reverse('users:api-v1:jwt-refresh'), data=body, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['access'] is not None
        assert response.data['access'] != access_token

    def test_verify_jwt_token(self, api_client, active_user):
        response = api_client.post(
            f'{self.url}', data={'email': 'serg@email.com', 'password': 'password'}
        )

        body = {'token': response.data['access']}

        response = api_client.post(
            path=reverse('users:api-v1:jwt-verify'),
            data=body,
        )

        assert response.status_code == status.HTTP_200_OK
