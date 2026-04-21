import sys
import json
import logging
import argparse

from dataclasses import dataclass, asdict
from functools import partial
from pathlib import Path


record = partial(dataclass, frozen=True, slots=True)
log = logging.getLogger('parse_users')


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


def parse_file(path: Path) -> list[tuple[int, User | ParseError]]:
    entries: list[tuple[int, User | ParseError]] = []
    for lineno, raw in enumerate(path.read_text().splitlines(), start=1):
        # Skip blank lines silently — they're not errors, they're padding.
        if not raw.strip():
            continue
        entries.append((lineno, parse_user(raw)))
    return entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='parse-users',
        description='Validate a file of name,email records and emit JSON.',
    )
    parser.add_argument('path', type=Path, help='Path to the user file.')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stderr)

    if not args.path.exists():
        log.error('file not found: %s', args.path)
        return 2

    entries = parse_file(args.path)
    users = [entry for _, entry in entries if isinstance(entry, User)]
    errors = [(lineno, entry) for lineno, entry in entries if isinstance(entry, ParseError)]

    # JSON to stdout; errors to stderr. Keeps the happy-path output pipeable.
    json.dump({'users': [asdict(u) for u in users]}, sys.stdout, indent=2)
    sys.stdout.write('\n')

    for lineno, err in errors:
        log.error('line %d: %s: %r', lineno, err.reason, err.line)

    return 1 if errors else 0
