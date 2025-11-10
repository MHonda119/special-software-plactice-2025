import time
import logging
from django.utils.deprecation import MiddlewareMixin


class RequestTimingMiddleware(MiddlewareMixin):
    """Logs requests exceeding a threshold.

    Threshold configurable via env REQUEST_TIME_WARN (seconds, default 2.0).
    Always logs total time at DEBUG level for traceability.
    """

    def process_request(self, request):  # noqa: D401
        request.__start_time = time.time()

    def process_response(self, request, response):
        start = getattr(request, "__start_time", None)
        if start is not None:
            elapsed = time.time() - start
            warn_threshold = 0.0
            # Derive threshold from env only (simplify & avoid long lines)
            import os

            try:
                warn_threshold = float(os.getenv("REQUEST_TIME_WARN", "2.0"))
            except ValueError:
                warn_threshold = 2.0
            logging.debug(
                "Request %s %s took %.3fs",
                request.method,
                request.path,
                elapsed,
            )
            if elapsed >= warn_threshold:
                logging.warning(
                    "Slow request %.3fs >= %.3fs %s %s",
                    elapsed,
                    warn_threshold,
                    request.method,
                    request.path,
                )
        return response

    def process_exception(self, request, exception):
        start = getattr(request, "__start_time", None)
        if start is not None:
            elapsed = time.time() - start
            logging.error(
                "Request exception after %.3fs %s %s: %s",
                elapsed,
                request.method,
                request.path,
                exception,
            )
        # Let Django continue normal exception handling
        return None
