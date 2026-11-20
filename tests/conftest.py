import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    application = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test.db"),
            "SEED_ON_START": False,
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seeded_app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "seeded.db"),
            "SEED_ON_START": True,
        }
    )


@pytest.fixture()
def seeded_client(seeded_app):
    return seeded_app.test_client()


def login_as(client, role: str = "leadership") -> dict:
    """Sign in through the real endpoint and return the user plus CSRF token."""
    response = client.post("/api/auth/session", json={"role": role})
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def csrf_headers(session: dict) -> dict:
    return {"X-CSRF-Token": session["csrf_token"]}
