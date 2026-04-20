from dataclasses import dataclass


@dataclass(frozen=True)
class NotFound:
    query: str


def find_first(items: list[str], query: str) -> str | NotFound:
    return next((x for x in items if x == query), NotFound(query))
