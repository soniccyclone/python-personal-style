import uvicorn

from bookmarks.api import create_app
from bookmarks.config import Settings
from bookmarks.logging import logged
from bookmarks.logging import configure_logging


@logged
def _run(settings: Settings) -> None:
    app = create_app(settings)
    uvicorn.run(app, host=settings.host, port=settings.port, log_config=None)


def main() -> None:
    settings = Settings()
    configure_logging(level=settings.log_level)
    _run(settings)
