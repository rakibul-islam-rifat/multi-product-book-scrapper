# logger_setup.py — one file per project
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(log_file="app.log", level=logging.DEBUG):
    root = logging.getLogger()

    if root.handlers:
        return

    root.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console — INFO and above
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    # File — DEBUG and above, rotates at 5MB
    file = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file.setLevel(logging.DEBUG)
    file.setFormatter(fmt)

    root.addHandler(console)
    root.addHandler(file)

    # Silence noisy libraries — add as needed
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("charset_normalizer").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("tzlocal").setLevel(logging.WARNING)
