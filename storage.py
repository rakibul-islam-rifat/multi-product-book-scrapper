import csv
import logging
from datetime import datetime
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)
root_folder: Path = Path(__file__).parent


def save_to_csv(books: list[dict], filename: str):
    csv_file = root_folder / f"{filename}.csv"

    with open(csv_file, "w", encoding="utf-8", newline="") as wf:
        writer = csv.DictWriter(
            wf,
            fieldnames=[
                "Timestamp",
                "Title",
                "Price",
                "Stock",
                "Rating",
                "Description",
                "Genre",
                "URL",
            ],
            restval="N/A",
            extrasaction="ignore",
        )

        logger.info("No existing file found, creating new: %s", csv_file.name)
        writer.writeheader()

        for book in books:
            row: dict = {
                **book,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            writer.writerow(row)

        logger.info("Saved %d new books to %s", len(books), csv_file.name)


def check_price_drop(book, threshold):
    price = book.get("Price")

    if price is None:
        logger.warning("No valid book price to compare.")
        return False

    return price < threshold
