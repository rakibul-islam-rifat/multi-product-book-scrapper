import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from logger_setup import setup_logging
from notifier import send_alert
from scrapper import scrape_all_book
from storage import check_price_drop, save_to_csv

setup_logging("Multi_Product.log")

logger = logging.getLogger(__name__)


def check_book(url: str, filename: str, threshold: float):
    try:
        books = scrape_all_book(url)
    except Exception as e:
        logger.error("Failed to grab the books, Cause: %s", e)
        return

    try:
        books_below_threshold: list[dict] = [
            book for book in books if check_price_drop(book, threshold)
        ]
        if not books_below_threshold:
            logger.info("No books below threshold — no email sent.")

        else:
            logger.info(
                "There are %d books priced below threshold",
                len(books_below_threshold),
            )

            subject: str = "Price Alert: Books Below Threshold"
            plain_body = html_body = ""

            for book in books_below_threshold:
                plain_body += (
                    f"{book['Title']}, Price: {book['Price']}, Url: {book['URL']}\n"
                )
                html_body += f"<p><b>{book['Title']}</b>, Price: <b>{book['Price']}</b>, Url: <b>{book['URL']}</b></p>\n"

            send_alert(subject, plain_body, html_body)

    except Exception as e:
        logger.error("Unable to send the email. Cause:- %s", e)

    logger.info("Saving all %d books to CSV (regardless of threshold)", len(books))
    save_to_csv(books, filename)


def main():
    url: str = input("Please input the url:- ").strip()
    if not url:
        logger.error("Invalid URL")
        return

    filename: str = input("Please input where you want to save your result:- ")
    if not filename.strip():
        logger.error("Invalid filename")
        return

    try:
        threshold = float(input("Please input your budget: "))
    except ValueError:
        logger.error("Invalid threshold input. Please enter a number.")
        return

    scheduler = BlockingScheduler()

    scheduler.add_job(
        func=check_book,
        trigger="cron",
        hour=9,
        minute=0,
        args=[url, filename, threshold],
        next_run_time=datetime.now(),
    )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.warning("\n\nScheduler stopped. Was checking everyday at 9 AM.\n\n")


if __name__ == "__main__":
    main()
