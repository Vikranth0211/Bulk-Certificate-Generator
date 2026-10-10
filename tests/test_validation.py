import pytest
from pydantic import ValidationError
from app.schemas.job import JobCreate, RecipientInput


def test_valid_recipient_input():
    recipient = RecipientInput(name="  John Doe  ", email="john@example.com  ")
    assert recipient.name == "John Doe"
    assert recipient.email == "john@example.com"


def test_blank_recipient_name_fails():
    with pytest.raises(ValidationError):
        RecipientInput(name="   ", email="john@example.com")


def test_invalid_email_format_fails():
    with pytest.raises(ValidationError):
        RecipientInput(name="John Doe", email="not-an-email-address")


def test_job_create_empty_recipients_fails():
    with pytest.raises(ValidationError):
        JobCreate(
            title="Test Title",
            event_name="Test Event",
            recipients=[]
        )
