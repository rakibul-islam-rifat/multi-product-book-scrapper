import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from fetch_urls import fetch_url

logger: logging.Logger = logging.getLogger(__name__)


def get_html(url) -> str:
    response = fetch_url(url)
    return response.text


def get_title(soup: BeautifulSoup) -> str | None:
    tag: Tag | None = soup.select_one("div.col-sm-6.product_main > h1")
    return tag.get_text(strip=True) if tag else None


def get_price(soup: BeautifulSoup) -> None | float:
    tag: Tag | None = soup.select_one("div.col-sm-6.product_main > p.price_color")

    if not tag:
        return None

    price_text: str = tag.get_text(strip=True)

    try:
        return float(price_text[1:])  # remove currency symbol
    except (ValueError, IndexError):
        return None


def stock_status(soup: BeautifulSoup) -> None | int:
    tag: Tag | None = soup.select_one("div.col-sm-6.product_main > p.instock")

    if not tag:
        return None

    text: str = tag.get_text(strip=True)

    try:
        return int(text.split("(")[1].split()[0])
    except (IndexError, ValueError):
        return None


def get_rating(soup: BeautifulSoup) -> None | str:
    tag: Tag | None = soup.select_one("div.col-sm-6.product_main > p.star-rating")

    if not tag:
        return None

    rating_text = tag.get("class")
    return rating_text[-1] if rating_text else None


def get_description(soup: BeautifulSoup) -> str | None:
    tag: Tag | None = soup.select_one("div#product_description ~ p")
    return tag.get_text(strip=True) if tag else None


def get_genre(soup: BeautifulSoup) -> str | None:
    tag = soup.select("ul.breadcrumb > li > a")

    return tag[2].get_text(strip=True) if len(tag) >= 3 else None


def get_next_page(soup: BeautifulSoup) -> str | None:
    tag: Tag | None = soup.select_one("li.next > a")
    return str(tag.get("href")) if tag else None


def get_book_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    tags = soup.select("h3 > a")
    return [urljoin(base_url, str(href)) for tag in tags if (href := tag.get("href"))]


def get_all_book_urls(base_url: str) -> list[str]:
    current_url: str | None = base_url
    urls: list[str] = []

    while current_url:
        source: str = get_html(current_url)
        soup = BeautifulSoup(source, "lxml")
        links: list[str] = get_book_links(soup, current_url)

        if links:
            urls.extend(links)

        next_page: str | None = get_next_page(soup)
        current_url = urljoin(current_url, next_page) if next_page else None

    logger.info("Successfully grabbed %d links", len(urls))
    return urls


def scrape_book(url: str) -> dict:
    source: str = get_html(url)
    soup = BeautifulSoup(source, "lxml")

    title: str | None = get_title(soup)
    price: None | float = get_price(soup)
    stock: None | int = stock_status(soup)
    rating: None | str = get_rating(soup)
    description: str | None = get_description(soup)
    genre: str | None = get_genre(soup)

    return {
        "Title": title,
        "Price": price,
        "Stock": stock,
        "Rating": rating,
        "Description": description,
        "Genre": genre,
        "URL": url,
    }


def scrape_all_book(base_url: str) -> list[dict]:
    all_urls: list[str] = get_all_book_urls(base_url)
    book_data: list[dict] = [scrape_book(url) for url in all_urls]
    logger.info(
        "Scraping finished, stored %d book data from %d urls.",
        len(book_data),
        len(all_urls),
    )
    return book_data
