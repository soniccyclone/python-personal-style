import sqlite3

from datetime import datetime

import pytest

from bookmarks.db import (
    Note,
    NotFound,
    create_schema,
    delete_note,
    get_note,
    insert_note,
    list_notes,
)


@pytest.fixture
def conn() -> sqlite3.Connection:
    connection = sqlite3.connect(':memory:')
    connection.row_factory = sqlite3.Row
    create_schema(connection)
    try:
        yield connection
    finally:
        connection.close()


def test_insert_note_returns_record_with_id_and_timestamp(conn):
    # Arrange
    content = 'first note'
    tags = ('python', 'style')

    # Act
    actual = insert_note(conn, content=content, tags=tags)

    # Assert
    assert actual.id == 1
    assert actual.content == content
    assert actual.tags == tags
    assert isinstance(actual.created_at, datetime)


def test_list_notes_returns_all_inserted(conn):
    # Arrange
    insert_note(conn, content='a', tags=('x',))
    insert_note(conn, content='b', tags=('y',))

    # Act
    actual = list_notes(conn)

    # Assert
    assert len(actual) == 2
    assert [n.content for n in actual] == ['a', 'b']


def test_list_notes_filters_by_tag(conn):
    # Arrange
    insert_note(conn, content='pythonic', tags=('python', 'style'))
    insert_note(conn, content='random', tags=('life',))
    insert_note(conn, content='another-py', tags=('python',))

    # Act
    actual = list_notes(conn, tag='python')

    # Assert
    assert [n.content for n in actual] == ['pythonic', 'another-py']


def test_get_note_returns_record_when_found(conn):
    # Arrange
    created = insert_note(conn, content='hello', tags=())

    # Act
    actual = get_note(conn, created.id)

    # Assert
    assert actual == created


def test_get_note_returns_not_found_when_missing(conn):
    # Arrange
    missing_id = 999

    # Act
    actual = get_note(conn, missing_id)

    # Assert
    assert actual == NotFound(note_id=missing_id)


def test_delete_note_returns_the_deleted_record(conn):
    # Arrange
    created = insert_note(conn, content='goodbye', tags=('bye',))

    # Act
    actual = delete_note(conn, created.id)

    # Assert
    assert actual == created
    assert get_note(conn, created.id) == NotFound(note_id=created.id)


def test_delete_note_returns_not_found_when_missing(conn):
    # Arrange
    missing_id = 42

    # Act
    actual = delete_note(conn, missing_id)

    # Assert
    assert actual == NotFound(note_id=missing_id)
