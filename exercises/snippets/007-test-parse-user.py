# pyright: reportUndefinedVariable=false, reportMissingImports=false
# User and parse_user would be imported from a sibling module in a
# real project; snippet files with hyphenated names aren't importable.
# pytest isn't installed in the snippets directory — the snippet
# exercises layout, not executable test runs.

import pytest


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

    # Act & Assert
    with pytest.raises(ValueError, match='malformed user line'):
        parse_user(line)


def test_parse_user_rejects_non_email():
    # Arrange
    line = 'alice,not-an-email'

    # Act & Assert
    with pytest.raises(ValueError, match='not an email'):
        parse_user(line)


@pytest.mark.parametrize('line', [
    '',
    'alice',
    'alice,',
    ',alice@example.com',
    'alice,no-at-sign',
])
def test_parse_user_rejects_malformed(line):
    # Act & Assert
    with pytest.raises(ValueError):
        parse_user(line)
