# SimplePushoverClient
A simple client for the Pushover notification service.

## Installation

```bash
pip install simplepushoverclient
```

## Usage

```python
from simplepushoverclient import PushoverClient, PushoverExceptionResponse

client = PushoverClient(token="my_token")  # optional: timeout=10 (seconds)

try:
    client.send(user="my_user", message="my_msg", device="device", title="title")
except PushoverExceptionResponse as e:
    print(f"Pushover rejected the message ({e.status_code}): {e.message}")
```

Network errors (e.g. timeouts) are raised as the usual `requests` exceptions.
