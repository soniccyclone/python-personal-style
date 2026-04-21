import pytest

# In a real project this imports from a sibling module; snippet
# files with hyphenated names aren't importable, so treat User and
# parse_user as if they were pulled from 006.


def test_parse_user_splits_name_and_email():
    user = parse_user('alice,alice@example.com')
    assert user == User(name='alice', email='alice@example.com')


def test_parse_user_strips_surrounding_whitespace():
    user = parse_user('  alice  ,  alice@example.com  ')
    assert user == User(name='alice', email='alice@example.com')


def test_parse_user_rejects_missing_comma():
    with pytest.raises(ValueError, match='malformed user line'):
        parse_user('just-a-name')


def test_parse_user_rejects_non_email():
    with pytest.raises(ValueError, match='not an email'):
        parse_user('alice,not-an-email')


@pytest.mark.parametrize('line', [
    '',
    'alice',
    'alice,',
    ',alice@example.com',
    'alice,no-at-sign',
])
def test_parse_user_rejects_malformed(line):
    with pytest.raises(ValueError):
        parse_user(line)
