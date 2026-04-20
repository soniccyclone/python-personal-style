def find_first(items: list[str], query: str) -> str | None:
    for item in items:
        if item == query:
            return item
    return None
