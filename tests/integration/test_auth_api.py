import pytest
from faker import Faker
from fastapi.testclient import TestClient

from src.main import bootstrap


fake = Faker()
integration = pytest.mark.integration


@pytest.fixture(scope='module')
def client():
    app = bootstrap()
    return TestClient(app)


@integration
def test_register_creates_user_successfully(client: TestClient) -> None:
    '''Registering with valid data should succeed and return a 2xx status.'''

    password = 'Str0ngP@ssw0rd!'
    payload = {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'password': password,
        'confirm_password': password,
    }

    response = client.post('/auth/register', json=payload)

    assert response.status_code in (200, 201)
    body = response.json()
    assert 'email' in body
    assert body['email'] == payload['email']


@integration
def test_register_validation_error_on_mismatched_passwords(client: TestClient) -> None:
    '''Mismatched password and confirm_password should yield a 4xx error.'''

    payload = {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'password': 'Str0ngP@ssw0rd!',
        'confirm_password': 'DifferentP@ssw0rd!',
    }

    response = client.post('/auth/register', json=payload)

    assert 400 <= response.status_code < 500


@integration
def test_register_duplicate_email_returns_conflict(client: TestClient) -> None:
    '''Registering the same email twice should return a conflict-style error on second attempt.'''

    password = 'Str0ngP@ssw0rd!'
    email = fake.email()
    payload = {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': email,
        'password': password,
        'confirm_password': password,
    }

    first_response = client.post('/auth/register', json=payload)
    second_response = client.post('/auth/register', json=payload)

    assert first_response.status_code in (200, 201)
    assert 400 <= second_response.status_code < 500


