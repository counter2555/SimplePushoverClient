import pytest

from simplepushoverclient.pushover import DEFAULT_TIMEOUT, PUSHOVER_API_URL, PushoverClient
from simplepushoverclient.exceptions import PushoverExceptionResponse

INVALID_TOKEN_ERROR = "application token is invalid, see https://pushover.net/api"
INVALID_USER_ERROR = (
    "user identifier is not a valid user, group, or subscribed user key, see https://pushover.net/api#identifiers"
)


def test_client_send_ok(requests_mock) -> None:
    # Arrange
    requests_mock.post(PUSHOVER_API_URL, status_code=200, json={"status": 1, "request": "abc-123"})

    client = PushoverClient(token="mytoken")

    # Act
    status = client.send("myuser", "Hello World", device="phone", title="Hi")

    # Assert
    assert status == 200
    assert requests_mock.last_request.json() == {
        "token": "mytoken",
        "user": "myuser",
        "device": "phone",
        "title": "Hi",
        "message": "Hello World",
    }


def test_client_send_uses_timeout(requests_mock) -> None:
    # Arrange
    requests_mock.post(PUSHOVER_API_URL, status_code=200, json={"status": 1})

    # Act
    PushoverClient(token="mytoken").send("myuser", "Hello World")
    PushoverClient(token="mytoken", timeout=3).send("myuser", "Hello World")

    # Assert
    assert requests_mock.request_history[0].timeout == DEFAULT_TIMEOUT
    assert requests_mock.request_history[1].timeout == 3


@pytest.mark.parametrize(
    "errors,expected_message",
    [
        (INVALID_TOKEN_ERROR, INVALID_TOKEN_ERROR),
        (INVALID_USER_ERROR, INVALID_USER_ERROR),
        ([INVALID_TOKEN_ERROR, "second error"], INVALID_TOKEN_ERROR),
        ([], ""),
    ],
)
def test_client_send_error(requests_mock, errors, expected_message: str) -> None:
    # Arrange
    requests_mock.post(
        PUSHOVER_API_URL,
        status_code=400,
        json={"token": "invalid", "errors": errors, "status": 0, "request": "abc-123"},
    )

    client = PushoverClient(token="mytoken")

    # Act
    with pytest.raises(PushoverExceptionResponse) as exc:
        client.send("myuser", "Hello World!")

    # Assert
    assert exc.value.status_code == 400
    assert exc.value.message == expected_message
    assert str(exc.value) == expected_message
    assert repr(exc.value) == f"400: {expected_message}"


def test_client_send_non_json_error(requests_mock) -> None:
    # Arrange
    requests_mock.post(PUSHOVER_API_URL, status_code=502, text="<html>Bad Gateway</html>")

    client = PushoverClient(token="mytoken")

    # Act
    with pytest.raises(PushoverExceptionResponse) as exc:
        client.send("myuser", "Hello World!")

    # Assert
    assert exc.value.status_code == 502
    assert exc.value.message == ""


def test_client_repr_hides_token() -> None:
    assert "mytoken" not in repr(PushoverClient(token="mytoken"))
