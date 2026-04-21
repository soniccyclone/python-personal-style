import sys
import logging
import inspect
import functools
import contextvars

import structlog


request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    'request_id', default=None
)

log = structlog.get_logger()


def add_request_id(logger, method_name, event_dict):
    request_id = request_id_var.get()
    if request_id is not None:
        event_dict['request_id'] = request_id
    return event_dict


def configure_logging(level: str = 'INFO') -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt='iso'),
            add_request_id,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    )


def logged(fn):
    sig = inspect.signature(fn)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        bound = dict(sig.bind(*args, **kwargs).arguments)
        log.debug('enter', function=fn.__name__, args=bound)
        try:
            result = fn(*args, **kwargs)
            log.debug('exit', function=fn.__name__, result=result)
            return result
        except Exception as exc:
            log.error(
                'error',
                function=fn.__name__,
                args=bound,
                exc_type=type(exc).__name__,
                exc_message=str(exc),
            )
            raise

    return wrapper
