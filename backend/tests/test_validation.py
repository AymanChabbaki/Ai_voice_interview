import pytest
from pydantic import ValidationError


def test_register_request_rejects_short_password(app_module):
    with pytest.raises(ValidationError):
        app_module.RegisterRequest(
            username="valid_user",
            email="u@example.com",
            password="short",
            name="Valid Name",
        )


def test_register_request_rejects_invalid_username(app_module):
    with pytest.raises(ValidationError):
        app_module.RegisterRequest(
            username="ab",
            email="u@example.com",
            password="longenoughpassword",
            name="Valid Name",
        )


def test_register_request_accepts_valid_payload(app_module):
    payload = app_module.RegisterRequest(
        username="valid_user_1",
        email="u@example.com",
        password="longenoughpassword",
        name="Valid Name",
    )
    assert payload.username == "valid_user_1"
