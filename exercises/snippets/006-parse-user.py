import logging

from dataclasses import dataclass
from functools import partial


record = partial(dataclass, frozen=True, slots=True)
log = logging.getLogger(__name__)


@record
class User:
    name: str
    email: str


def parse_user(line: str) -> User:
    """Parse a 'name,email' line into a User."""
    # Bail early on malformed input rather than half-parse.
    parts = line.strip().split(',', 1)
    if len(parts) != 2:
        raise ValueError(f'malformed user line: {line!r}')

    name, email = parts
    _require_email(email)
    return User(name=name.strip(), email=email.strip())


def _require_email(email: str) -> None:
    if '@' not in email.strip():
        raise ValueError(f'not an email: {email!r}')
