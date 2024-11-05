import secrets
from datetime import (
    datetime,
    timezone,
)


def now() -> datetime:
    """
    Returns the current time in UTC.
    :return: datetime: datetime (in UTC.)
    """
    return datetime.now(tz=timezone.utc)


def generate_random_string(size: int = 32, alphabet: str = tuple(chr(x) for x in range(33, 127))) -> str:
    """
    Generates a random string of given length.
    :param size:
    :param alphabet:
    :return: random_string: str
    """
    return "".join(secrets.choice(alphabet) for _ in range(size))
