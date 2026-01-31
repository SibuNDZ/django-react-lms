from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

User = get_user_model()


class UserRegistrationTests(APITestCase):
    """Tests for user registration endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/user/register/'

    def test_register_user_success(self):
        """Test successful user registration"""
        data = {
            'full_name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())

    def test_register_user_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        data = {
            'full_name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass123!'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_weak_password(self):
        """Test registration fails with weak password"""
        data = {
            'full_name': 'Test User',
            'email': 'testuser@example.com',
            'password': '123',
            'password2': '123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_duplicate_email(self):
        """Test registration fails with duplicate email"""
        User.objects.create_user(
            email='existing@example.com',
            password='ExistingPass123!',
            username='existing'
        )
        data = {
            'full_name': 'New User',
            'email': 'existing@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_missing_fields(self):
        """Test registration fails with missing required fields"""
        data = {
            'email': 'testuser@example.com',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    """Tests for user login (token obtain) endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.token_url = '/api/v1/user/token/'
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPass123!',
            username='testuser',
            full_name='Test User'
        )

    def test_login_success(self):
        """Test successful login returns tokens"""
        data = {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login fails for non-existent user"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_token_contains_user_data(self):
        """Test that token contains expected user claims"""
        import jwt
        from django.conf import settings

        data = {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.token_url, data, format='json')
        access_token = response.data['access']

        # Decode without verification to check claims
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        self.assertEqual(decoded['email'], 'testuser@example.com')
        self.assertEqual(decoded['full_name'], 'Test User')
        self.assertEqual(decoded['username'], 'testuser')


class TokenRefreshTests(APITestCase):
    """Tests for token refresh endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.token_url = '/api/v1/user/token/'
        self.refresh_url = '/api/v1/user/token/refresh/'
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPass123!',
            username='testuser'
        )

    def test_refresh_token_success(self):
        """Test successful token refresh"""
        # First, get tokens
        login_response = self.client.post(self.token_url, {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }, format='json')
        refresh_token = login_response.data['refresh']

        # Then refresh
        response = self.client.post(self.refresh_url, {
            'refresh': refresh_token
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_token_invalid(self):
        """Test refresh fails with invalid token"""
        response = self.client.post(self.refresh_url, {
            'refresh': 'invalid-token'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordTests(APITestCase):
    """Tests for authenticated password change endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.change_password_url = '/api/v1/user/change-password/'
        self.token_url = '/api/v1/user/token/'
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='OldPassword123!',
            username='testuser'
        )

    def get_auth_token(self):
        response = self.client.post(self.token_url, {
            'email': 'testuser@example.com',
            'password': 'OldPassword123!'
        }, format='json')
        return response.data['access']

    def test_change_password_success(self):
        """Test successful password change for authenticated user"""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.post(self.change_password_url, {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword456!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify new password works
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword456!'))

    def test_change_password_wrong_old_password(self):
        """Test password change fails with wrong old password"""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.post(self.change_password_url, {
            'old_password': 'WrongOldPassword!',
            'new_password': 'NewPassword456!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        """Test password change fails without authentication"""
        response = self.client.post(self.change_password_url, {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword456!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetTests(APITestCase):
    """Tests for password reset flow"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPass123!',
            username='testuser'
        )

    def test_password_reset_request_existing_user(self):
        """Test password reset request for existing user"""
        url = '/api/v1/user/password-reset/testuser@example.com/'
        response = self.client.get(url)
        # Should return user data (or None if not found)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_password_reset_request_sets_otp(self):
        """Test that password reset sets OTP on user"""
        url = '/api/v1/user/password-reset/testuser@example.com/'
        self.client.get(url)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.otp)
        self.assertEqual(len(self.user.otp), 7)  # OTP is 7 digits

    def test_password_change_with_otp(self):
        """Test password change using OTP"""
        # First, request password reset to get OTP
        reset_url = '/api/v1/user/password-reset/testuser@example.com/'
        self.client.get(reset_url)

        self.user.refresh_from_db()
        otp = self.user.otp

        # Now change password
        change_url = '/api/v1/user/password-change/'
        response = self.client.post(change_url, {
            'otp': otp,
            'uuidb64': self.user.pk,
            'password': 'NewSecurePassword123!'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify OTP is cleared
        self.user.refresh_from_db()
        self.assertEqual(self.user.otp, '')

    def test_password_change_invalid_otp(self):
        """Test password change fails with invalid OTP"""
        change_url = '/api/v1/user/password-change/'
        response = self.client.post(change_url, {
            'otp': '1234567',
            'uuidb64': self.user.pk,
            'password': 'NewSecurePassword123!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RateLimitingTests(APITestCase):
    """Tests for rate limiting on auth endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.token_url = '/api/v1/user/token/'

    def test_rate_limiting_exists(self):
        """Test that rate limiting is configured (basic check)"""
        from django.conf import settings
        self.assertIn('DEFAULT_THROTTLE_RATES', settings.REST_FRAMEWORK)
        self.assertIn('anon', settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'])
