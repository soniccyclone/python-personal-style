"""Small greeting helper — nitpick fodder for snippet 001."""
from typing import Optional


def greet(name: str, greeting: Optional[str] = None) -> str:
    """Return a greeting for the given name.

    Args:
        name: Person to greet.
        greeting: Optional custom salutation. Defaults to "Hello".

    Returns:
        The formatted greeting.
    """
    if greeting is None:
        greeting = "Hello"
    return f"{greeting}, {name}!"


if __name__ == "__main__":
    print(greet("Nathan"))
    print(greet("Nathan", greeting="Howdy"))
