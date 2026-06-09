import os
from django.conf import settings


def get_supabase_client():
    """Return a Supabase client. Falls back to mock if not configured."""
    url = getattr(settings, 'SUPABASE_URL', '') or os.getenv('SUPABASE_URL', '')
    key = getattr(settings, 'SUPABASE_KEY', '') or os.getenv('SUPABASE_KEY', '')

    if not url or not key:
        return MockSupabaseClient()

    try:
        from supabase import create_client
        return create_client(url, key)
    except ImportError:
        return MockSupabaseClient()


class MockUser:
    def __init__(self, email, is_admin=True):
        self.id = "mock-admin-uuid-123456"
        self.email = email
        self.user_metadata = {"is_admin": is_admin}


class MockSession:
    def __init__(self):
        self.access_token = "mock-access-token-xyz"
        self.refresh_token = "mock-refresh-token-xyz"


class MockAuthResponse:
    def __init__(self, email, is_admin=True):
        self.user = MockUser(email, is_admin)
        self.session = MockSession()


class MockAuth:
    def sign_in_with_password(self, credentials):
        email = credentials.get("email", "")
        password = credentials.get("password", "")
        # Accept admin@scentsensation.com / admin123
        if email.lower().startswith("admin") and password in ("admin123", "adminpass", "adminpassword"):
            return MockAuthResponse(email, is_admin=True)
        raise Exception("Invalid login credentials")

    def sign_out(self):
        return True


class MockSupabaseClient:
    def __init__(self):
        self.auth = MockAuth()
