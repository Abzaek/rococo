"""
Test cases for token validation crash fix in rococo.auth.tokens.

validate_confirmation_token and validate_access_token must return False on
malformed input rather than raising.
"""

import hashlib
import hmac
import time

import pytest

from rococo.auth.tokens import (
    generate_access_token,
    generate_confirmation_token,
    validate_access_token,
    validate_confirmation_token,
)


SECRET_KEY = "test-secret"
EXPIRATION = 3600


def _craft_token(identifier: str, timestamp: int, secret_key: str = SECRET_KEY) -> str:
    """Build a token with an arbitrary timestamp so we can simulate expiry."""
    data = identifier + str(timestamp)
    signature = hmac.new(
        key=secret_key.encode("utf-8"),
        msg=data.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return f"{identifier}:{timestamp}:{signature}"


class TestValidateConfirmationToken:
    def test_none_returns_false(self):
        assert validate_confirmation_token(None, SECRET_KEY, EXPIRATION) is False

    def test_no_colons_returns_false(self):
        assert validate_confirmation_token("not-a-token", SECRET_KEY, EXPIRATION) is False

    def test_non_numeric_timestamp_returns_false(self):
        assert validate_confirmation_token("user:abc:sig", SECRET_KEY, EXPIRATION) is False

    def test_valid_token_returns_email(self):
        email = "user@example.com"
        token = generate_confirmation_token(email, SECRET_KEY)
        assert validate_confirmation_token(token, SECRET_KEY, EXPIRATION) == email

    def test_expired_token_returns_false(self):
        email = "user@example.com"
        old_timestamp = int(time.time()) - (EXPIRATION + 60)
        token = _craft_token(email, old_timestamp)
        assert validate_confirmation_token(token, SECRET_KEY, EXPIRATION) is False


class TestValidateAccessToken:
    def test_none_returns_false(self):
        assert validate_access_token(None, SECRET_KEY, EXPIRATION) is False

    def test_no_colons_returns_false(self):
        assert validate_access_token("not-a-token", SECRET_KEY, EXPIRATION) is False

    def test_non_numeric_timestamp_returns_false(self):
        assert validate_access_token("user:abc:sig", SECRET_KEY, EXPIRATION) is False

    def test_valid_token_returns_entity_id(self):
        entity_id = "entity-123"
        token, _ = generate_access_token(entity_id, SECRET_KEY, EXPIRATION)
        assert validate_access_token(token, SECRET_KEY, EXPIRATION) == entity_id

    def test_expired_token_returns_false(self):
        entity_id = "entity-123"
        old_timestamp = int(time.time()) - (EXPIRATION + 60)
        token = _craft_token(entity_id, old_timestamp)
        assert validate_access_token(token, SECRET_KEY, EXPIRATION) is False
