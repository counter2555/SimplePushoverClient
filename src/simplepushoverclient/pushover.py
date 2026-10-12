from typing import Optional

import requests

from simplepushoverclient.exceptions import PushoverExceptionResponse
from simplepushoverclient.models import SendMessageModel

PUSHOVER_API_URL: str = "https://api.pushover.net/1/messages.json"
DEFAULT_TIMEOUT: float = 10.0


class PushoverClient:
    """A client for sending Pushover messages"""

    token: str
    timeout: float

    def __init__(self, token: str, timeout: float = DEFAULT_TIMEOUT):
        """initializes the Pushover client

        Args:
            token (str): Pushover API Token
            timeout (float, optional): request timeout in seconds. Defaults to 10.
        """
        self.token = token
        self.timeout = timeout

    def __repr__(self) -> str:
        # never expose the API token in logs or tracebacks
        return f"{type(self).__name__}(token='***', timeout={self.timeout})"

    def send(
        self,
        user: str,
        message: str,
        device: Optional[str] = None,
        title: Optional[str] = None,
    ) -> int:
        """Sends a message via Pushover to the user.

        Args:
            user (str): user key to send message to
            message (str): message content
            device (str, optional): device to message. Defaults to None.
            title (str, optional): title of the message. Defaults to None.

        Raises:
            PushoverExceptionResponse: if the API does not respond with HTTP 200

        Returns:
            int: HTTP status code
        """
        model = SendMessageModel(token=self.token, user=user, message=message, device=device, title=title)

        response = requests.post(PUSHOVER_API_URL, json=model.dump(), timeout=self.timeout)

        if response.status_code != 200:
            raise PushoverExceptionResponse(
                status_code=response.status_code,
                message=_parse_error(response),
            )
        return response.status_code


def _parse_error(response: requests.Response) -> str:
    """extracts the first error message from a Pushover error response

    Args:
        response (requests.Response): the failed response

    Returns:
        str: error message, or an empty string if none could be parsed
    """
    try:
        errors = response.json().get("errors")
    except (ValueError, AttributeError):
        # body is not a JSON object (e.g. an HTML error page from a proxy)
        return ""

    if isinstance(errors, list):
        return str(errors[0]) if errors else ""
    if isinstance(errors, str):
        return errors
    return ""
