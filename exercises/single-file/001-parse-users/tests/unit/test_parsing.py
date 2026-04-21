import io

import pytest
from hypothesis import given, strategies as st

from parse_users import User, ParseError, parse_user, parse


# Fragments valid inside a user line: non-empty after stripping, no commas,
# no internal newlines (parse_file splits on those).
valid_fragments = st.text(
    alphabet=st.characters(blacklist_characters=',\n\r'),
    min_size=1,
).filter(lambda s: s.strip())


@given(name=valid_fragments, local=valid_fragments, domain=valid_fragments)
def test_parse_user_roundtrips_valid_input(name, local, domain):
    # Arrange
    email = f'{local}@{domain}'
    line = f'{name},{email}'
    expected = User(name=name.strip(), email=email.strip())

    # Act
    actual = parse_user(line)

    # Assert
    assert actual == expected


def test_parse_user_splits_name_and_email():
    # Arrange
    line = 'alice,alice@example.com'
    expected = User(name='alice', email='alice@example.com')

    # Act
    actual = parse_user(line)

    # Assert
    assert actual == expected


def test_parse_user_strips_surrounding_whitespace():
    # Arrange
    line = '  alice  ,  alice@example.com  '
    expected = User(name='alice', email='alice@example.com')

    # Act
    actual = parse_user(line)

    # Assert
    assert actual == expected


def test_parse_user_rejects_missing_comma():
    # Arrange
    line = 'just-a-name'

    # Act
    actual = parse_user(line)

    # Assert
    assert actual == ParseError(line='just-a-name', reason='malformed user line')


def test_parse_user_rejects_non_email():
    # Arrange
    line = 'alice,not-an-email'

    # Act
    actual = parse_user(line)

    # Assert
    assert actual == ParseError(line='alice,not-an-email', reason='not an email')


@pytest.mark.parametrize('line, reason', [
    ('', 'malformed user line'),
    ('alice', 'malformed user line'),
    ('alice,', 'not an email'),
    (',alice@example.com', 'not an email'),
    ('alice,no-at-sign', 'not an email'),
])
def test_parse_user_rejects_malformed(line, reason):
    # Act
    actual = parse_user(line)

    # Assert
    assert isinstance(actual, ParseError)
    assert actual.reason == reason


def test_parse_interleaves_users_and_errors_from_a_stream():
    # Arrange
    source = io.StringIO(
        'alice,alice@example.com\n'
        'bad-line\n'
        'bob,bob@example.com\n'
        '\n'
        'carol,no-at\n'
    )
    expected = [
        (1, User(name='alice', email='alice@example.com')),
        (2, ParseError(line='bad-line', reason='malformed user line')),
        (3, User(name='bob', email='bob@example.com')),
        (5, ParseError(line='carol,no-at', reason='not an email')),
    ]

    # Act
    actual = list(parse(source))

    # Assert
    assert actual == expected


def test_parse_skips_blank_lines_without_erroring():
    # Arrange
    source = io.StringIO('\n\n\nalice,alice@example.com\n\n')
    expected = [(4, User(name='alice', email='alice@example.com'))]

    # Act
    actual = list(parse(source))

    # Assert
    assert actual == expected
