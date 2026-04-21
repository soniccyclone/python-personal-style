import json

from parse_users import main


def test_main_emits_json_for_valid_users(tmp_path, capsys):
    # Arrange
    source = tmp_path / 'users.txt'
    source.write_text('alice,alice@example.com\nbob,bob@example.com\n')

    # Act
    exit_code = main([str(source)])

    # Assert
    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        'users': [
            {'name': 'alice', 'email': 'alice@example.com'},
            {'name': 'bob', 'email': 'bob@example.com'},
        ]
    }


def test_main_returns_1_when_any_record_fails(tmp_path, capsys):
    # Arrange
    source = tmp_path / 'users.txt'
    source.write_text('alice,alice@example.com\nbad-line\n')

    # Act
    exit_code = main([str(source)])

    # Assert
    captured = capsys.readouterr()
    assert exit_code == 1
    assert json.loads(captured.out) == {
        'users': [{'name': 'alice', 'email': 'alice@example.com'}]
    }
    assert 'bad-line' in captured.err


def test_main_returns_2_when_file_missing(tmp_path):
    # Arrange
    missing = tmp_path / 'nope.txt'

    # Act
    exit_code = main([str(missing)])

    # Assert
    assert exit_code == 2
