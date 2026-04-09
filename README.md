# 📚 Multi-Product Book Scraper

A Python automation tool that scrapes all 1000 books from [Books to Scrape](https://books.toscrape.com), monitors prices against a user-defined threshold, sends email alerts for books below budget, and saves complete book data to CSV — running automatically every 6 hours.

---

## Features

- Scrapes all 50 listing pages automatically via pagination
- Visits each of the 1000 individual book pages (spider pattern)
- Extracts title, price, stock count, rating, description, and genre
- Detects books priced below a user-defined threshold
- Sends email alerts listing all books below threshold
- Saves complete dataset to CSV on every run
- Retry logic with exponential backoff for network failures
- Rate limiting between requests to avoid server bans
- Structured logging to both console and rotating log file

---

## Project Structure

```
multi-product-scraper/
├── main.py          # Entry point — scheduler and orchestration
├── fetch_urls.py    # HTTP requests with retry and rate limiting
├── scrapper.py      # BeautifulSoup HTML parsing — listing + detail pages
├── storage.py       # CSV storage and price threshold checking
├── notifier.py      # Email alerts via smtplib
├── logger_setup.py  # Logging configuration
├── .env             # Credentials (never committed)
├── .env.example     # Template for credentials
├── .gitignore
└── README.md
```

---

## How It Works

The scraper uses a **spider pattern**:

1. Starts at the listing page and follows pagination across all 50 pages
2. Collects all 1000 individual book URLs
3. Visits each book's detail page and extracts full data
4. Filters books below your price threshold
5. Sends an email alert if any are found
6. Saves the complete dataset to CSV

This runs immediately on start, then repeats every 6 hours.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/multi-product-scraper.git
cd multi-product-scraper
```

### 2. Install dependencies

This project uses [uv](https://github.com/astral-sh/uv) for package management.

```bash
uv sync
```

Or with pip:

```bash
pip install -r requirements.txt
```

### 3. Configure credentials

```bash
cp .env.example .env
```

Open `.env` and add your Gmail credentials:

```
EMAIL=your_email@gmail.com
APP_PASSWORD=your_16_character_app_password
```

> **Important:** Use a Gmail App Password, not your real Gmail password. See [how to generate one](https://support.google.com/accounts/answer/185833).

### 4. Run

```bash
python main.py
```

You will be prompted for:

- **URL** — the starting URL (e.g. `https://books.toscrape.com/catalogue/page-1.html`)
- **Output filename** — name of the CSV file (e.g. `books` — saves as `books.csv`)
- **Price threshold** — your budget in GBP (e.g. `15.00`)

---

## Example Output

**CSV (`books.csv`):**

```
Timestamp,Title,Price,Stock,Rating,Description,Genre,URL
2026-04-04 12:00:00,A Light in the Attic,51.77,22,Three,"It's hard to love...",Poetry,https://...
2026-04-04 12:00:00,Tipping the Velvet,53.74,1,One,"A love story...",Historical Fiction,https://...
```

**Email alert:**

> **Price Alert: Books Below Threshold**
>
> Sharp Objects, Price: 4.61, Url: https://...
> Soumission, Price: 11.72, Url: https://...

---

## Performance

Scraping all 1000 books makes approximately 1050 requests total (50 listing pages + 1000 detail pages). With a 3 second delay between requests this takes around **50 minutes per run**. This is intentional — the delay prevents the scraper from being blocked by the server.

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP requests |
| `beautifulsoup4` | HTML parsing |
| `lxml` | HTML parser backend |
| `apscheduler` | Job scheduling |
| `python-dotenv` | Credentials from `.env` |

---

## Notes

- This project scrapes [Books to Scrape](https://books.toscrape.com) — a sandbox site built for scraping practice.
- Email alerts require a Gmail account with 2-Step Verification enabled.
- The CSV is overwritten on each run — it reflects the current state of the site, not a historical log.
- To change the schedule interval, modify `hours=6` in `main.py`.