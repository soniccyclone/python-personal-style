import time
import sqlite3

from uuid import uuid4
from datetime import datetime
from typing import Annotated, Iterator

import structlog

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from bookmarks.db import (
    Note,
    NotFound,
    connect,
    create_schema,
    delete_note,
    get_note,
    insert_note,
    list_notes,
)
from bookmarks.config import Settings
from bookmarks.logging import request_id_var


log = structlog.get_logger()


class NoteCreate(BaseModel):
    content: str
    tags: list[str] = []


class NoteOut(BaseModel):
    id: int
    content: str
    tags: list[str]
    created_at: datetime

    @classmethod
    def from_record(cls, note: Note) -> 'NoteOut':
        return cls(
            id=note.id,
            content=note.content,
            tags=list(note.tags),
            created_at=note.created_at,
        )


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title='bookmarks', version='0.1.0')
    app.state.settings = settings

    _ensure_schema(settings)
    _register_middleware(app)
    _register_routes(app)

    return app


def _ensure_schema(settings: Settings) -> None:
    conn = connect(settings.db_path)
    try:
        create_schema(conn)
    finally:
        conn.close()


def _register_middleware(app: FastAPI) -> None:
    @app.middleware('http')
    async def request_id_and_logging(request: Request, call_next):
        request_id = request.headers.get('X-Request-ID') or str(uuid4())
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        log.info('request_start', method=request.method, path=request.url.path)
        try:
            response = await call_next(request)
        except Exception as exc:
            log.error(
                'request_error',
                method=request.method,
                path=request.url.path,
                exc_type=type(exc).__name__,
                exc_message=str(exc),
            )
            raise
        finally:
            request_id_var.reset(token)

        duration_ms = (time.perf_counter() - started) * 1000
        log.info(
            'request_end',
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        response.headers['X-Request-ID'] = request_id
        return response


def _register_routes(app: FastAPI) -> None:
    def get_db() -> Iterator[sqlite3.Connection]:
        settings: Settings = app.state.settings
        conn = connect(settings.db_path)
        try:
            yield conn
        finally:
            conn.close()

    Db = Annotated[sqlite3.Connection, Depends(get_db)]

    @app.post('/notes', response_model=NoteOut, status_code=201)
    def create(payload: NoteCreate, db: Db) -> NoteOut:
        note = insert_note(db, content=payload.content, tags=tuple(payload.tags))
        return NoteOut.from_record(note)

    @app.get('/notes', response_model=list[NoteOut])
    def list_all(db: Db, tag: str | None = None) -> list[NoteOut]:
        return [NoteOut.from_record(n) for n in list_notes(db, tag=tag)]

    @app.get('/notes/{note_id}', response_model=NoteOut)
    def get_one(note_id: int, db: Db) -> NoteOut:
        result = get_note(db, note_id)
        if isinstance(result, NotFound):
            raise HTTPException(status_code=404, detail='note not found')
        return NoteOut.from_record(result)

    @app.delete('/notes/{note_id}', response_model=NoteOut)
    def delete(note_id: int, db: Db) -> NoteOut:
        result = delete_note(db, note_id)
        if isinstance(result, NotFound):
            raise HTTPException(status_code=404, detail='note not found')
        return NoteOut.from_record(result)

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception) -> JSONResponse:
        log.error('unhandled_exception', exc_type=type(exc).__name__, exc_message=str(exc))
        return JSONResponse(status_code=500, content={'detail': 'internal server error'})
