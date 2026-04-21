import json
import sqlite3

from datetime import datetime, timezone
from pathlib import Path

from bookmarks._record import record


@record
class Note:
    id: int
    content: str
    tags: tuple[str, ...]
    created_at: datetime


@record
class NotFound:
    note_id: int


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            content    TEXT NOT NULL,
            tags       TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL
        );
    ''')
    conn.commit()


def insert_note(conn: sqlite3.Connection, content: str, tags: tuple[str, ...]) -> Note:
    created_at = datetime.now(timezone.utc)
    cursor = conn.execute(
        'INSERT INTO notes (content, tags, created_at) VALUES (?, ?, ?)',
        (content, json.dumps(list(tags)), created_at.isoformat()),
    )
    conn.commit()
    note_id = cursor.lastrowid
    assert note_id is not None
    return Note(id=note_id, content=content, tags=tags, created_at=created_at)


def list_notes(conn: sqlite3.Connection, tag: str | None = None) -> list[Note]:
    if tag is None:
        rows = conn.execute(
            'SELECT id, content, tags, created_at FROM notes ORDER BY id'
        ).fetchall()
    else:
        rows = conn.execute(
            '''SELECT id, content, tags, created_at FROM notes
               WHERE EXISTS (SELECT 1 FROM json_each(tags) WHERE value = ?)
               ORDER BY id''',
            (tag,),
        ).fetchall()
    return [_row_to_note(row) for row in rows]


def get_note(conn: sqlite3.Connection, note_id: int) -> Note | NotFound:
    row = conn.execute(
        'SELECT id, content, tags, created_at FROM notes WHERE id = ?',
        (note_id,),
    ).fetchone()
    if row is None:
        return NotFound(note_id=note_id)
    return _row_to_note(row)


def delete_note(conn: sqlite3.Connection, note_id: int) -> Note | NotFound:
    existing = get_note(conn, note_id)
    if isinstance(existing, NotFound):
        return existing
    conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    return existing


def _row_to_note(row: sqlite3.Row) -> Note:
    return Note(
        id=row['id'],
        content=row['content'],
        tags=tuple(json.loads(row['tags'])),
        created_at=datetime.fromisoformat(row['created_at']),
    )
