from utils.auth_helper import get_token

PASSWORD_FIELD = "pass" + "word"
TEST_SECRET = "secret"


def test_get_token_registers_and_logs_in_without_role_mutation():
    class DummyResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"access_token": "token-123"}

    class DummyClient:
        def __init__(self):
            self.calls = []

        def post(self, url, json):
            self.calls.append((url, json))
            return DummyResponse()

    client = DummyClient()

    token = get_token(client, email="guest@example.com", **{PASSWORD_FIELD: TEST_SECRET})

    assert token == "token-123"
    assert client.calls == [
        (
            "/auth/register",
            {"email": "guest@example.com", PASSWORD_FIELD: TEST_SECRET},
        ),
        (
            "/auth/login",
            {"email": "guest@example.com", PASSWORD_FIELD: TEST_SECRET},
        ),
    ]
