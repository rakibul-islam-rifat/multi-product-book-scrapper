import logging
import time
from functools import wraps

import requests

logger: logging.Logger = logging.getLogger(__name__)

my_headers: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def add_delay(delay=2):
    def decorator(func):
        last_called: float | None = None

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_called

            if last_called is not None:
                elapsed: float = time.time() - last_called

                if elapsed < delay:
                    wait = delay - elapsed
                    logger.debug("Waiting %.2fs before next run ...", wait)
                    time.sleep(wait)

            result = func(*args, **kwargs)
            last_called = time.time()
            return result

        return wrapper

    return decorator


def _handle_error(attempt: int, msg: str, wait: int) -> None:
    logger.warning("Attempt %d failed: %s, waiting %ds ...", attempt, msg, wait)
    time.sleep(wait)


@add_delay(delay=3)
def fetch_url(url: str, payload: dict | None = None, max_attempts: int = 3):
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            response: requests.Response = requests.get(
                url, headers=my_headers, params=payload, timeout=10
            )
            response.raise_for_status()
            response.encoding = "utf-8"
            return response

        except requests.exceptions.ConnectionError as e:
            last_error = e
            _handle_error(attempt, "Connection Failed", 2**attempt)

        except requests.exceptions.Timeout as e:
            last_error = e
            _handle_error(attempt, "Timed Out", 2)

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            if status_code and (status_code == 429 or status_code >= 500):
                last_error = e
                _handle_error(attempt, f"Server Failed: {status_code}", 2)
            else:
                logger.error("Bad requests: %d", status_code)
                raise

    logger.warning("All %d attempts failed. Last Error: %s", max_attempts, last_error)
    raise RuntimeError(f"All {max_attempts} failed. Last Error {last_error}")
