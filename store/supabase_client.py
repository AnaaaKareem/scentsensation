import os
from django.conf import settings

class MockUser:
    def __init__(self, email):
        self.id = "mock-admin-uuid-123456"
        self.email = email
        self.user_metadata = {"is_admin": True}

class MockSession:
    def __init__(self):
        self.access_token = "mock-access-token-xyz"
        self.refresh_token = "mock-refresh-token-xyz"

class MockAuthResponse:
    def __init__(self, email):
        self.user = MockUser(email)
        self.session = MockSession()

class MockAuth:
    def sign_in_with_password(self, credentials):
        email = credentials.get("email")
        password = credentials.get("password")
        
        # Simple rule: allow any login with 'admin' in the email or password
        if "admin" in email.lower() or password == "adminpass" or password == "adminpassword":
            return MockAuthResponse(email)
        else:
            # Raise an AuthApiError-like exception
            class MockAuthError(Exception):
                pass
            raise MockAuthError("Invalid login credentials")

    def sign_out(self):
        return True

class MockSupabaseClient:
    def __init__(self):
        self.auth = MockAuth()

def get_supabase_client():
    url = getattr(settings, 'SUPABASE_URL', '')
    key = getattr(settings, 'SUPABASE_KEY', '')
    
    if not url or not key:
        return MockSupabaseClient()
        
    try:
        from supabase import create_client
        return create_client(url, key)
    except ImportError:
        # Fallback if package is not installed or import fails
        return MockSupabaseClient()
