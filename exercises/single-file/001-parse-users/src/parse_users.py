import sys
import json
import inspect
import argparse
import functools

from dataclasses import dataclass, asdict
from functools import partial
from pathlib import Path
from typing import Iterator, TextIO

import structlog


record = partial(dataclass, frozen=True, slots=True)


structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
)

log = structlog.get_logger()


@record
class User:
    name: str
    email: str


@record
class ParseError:
    line: str
    reason: str


def parse_user(line: str) -> User | ParseError:
    parts = line.strip().split(',', 1)
    if len(parts) != 2:
        return ParseError(line=line, reason='malformed user line')

    name, email = parts
    if '@' not in email.strip():
        return ParseError(line=line, reason='not an email')

    return User(name=name.strip(), email=email.strip())


def parse(source: TextIO) -> Iterator[tuple[int, User | ParseError]]:
    for lineno, raw in enumerate(source, start=1):
        # Skip blank lines silently — they're padding, not records.
        if not raw.strip():
            continue
        yield (lineno, parse_user(raw.rstrip('\n')))


def logged(fn):
    sig = inspect.signature(fn)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        bound = dict(sig.bind(*args, **kwargs).arguments)
        log.debug('enter', function=fn.__name__, args=bound)
        try:
            result = fn(*args, **kwargs)
            log.debug('exit', function=fn.__name__, result=result)
            return result
        except Exception as exc:
            log.error(
                'error',
                function=fn.__name__,
                args=bound,
                exc_type=type(exc).__name__,
                exc_message=str(exc),
            )
            raise
    return wrapper


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='parse-users',
        description='Validate a file of name,email records and emit JSON.',
    )
    parser.add_argument('path', type=Path, help='Path to the user file.')
    return parser.parse_args(argv)


def emit_json(payload: dict) -> None:
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write('\n')


def _collect(path: Path) -> tuple[list[User], list[tuple[int, ParseError]]]:
    users: list[User] = []
    errors: list[tuple[int, ParseError]] = []
    with path.open() as source:
        for lineno, entry in parse(source):
            if isinstance(entry, User):
                users.append(entry)
            else:
                errors.append((lineno, entry))
    return users, errors


def _report_errors(errors: list[tuple[int, ParseError]]) -> None:
    for lineno, err in errors:
        log.warning('parse_error', lineno=lineno, line=err.line, reason=err.reason)


@logged
def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.path.exists():
        log.error('file_not_found', path=str(args.path))
        return 2

    users, errors = _collect(args.path)
    emit_json({'users': [asdict(u) for u in users]})
    _report_errors(errors)

    return 1 if errors else 0
