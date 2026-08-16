# Web Scraping Backend Practice – SQLite Persistence

A production-inspired backend project for robust web scraping with local SQLite persistence. Built as a structured learning exercise to master core backend concepts: defensive HTML parsing, pagination handling, data normalization with pandas, atomic database writes, and client-ready data export.

## Overview

This project scrapes structured web data (e.g., product listings, job postings, market data) using **BeautifulSoup**, cleans and normalizes it with **pandas**, and persists results to a local **SQLite database**. It demonstrates full data pipeline fundamentals: robust error handling, pagination, data validation, transaction management, and JSON/CSV export.

### Key Features

- **Robust Web Scraping** with defensive parsing and error recovery
- **Pagination Support** for multi-page datasets
- **Data Normalization** with pandas (cleaning, deduplication, type coercion)
- **SQLite Persistence** with atomic transactions and schema design
- **JSON & CSV Export** for client-ready deliverables
- **Error Logging** with graceful fallbacks
- **Rate Limiting** to respect server load

---

## Architecture

### Learning Phases

| Phase | Focus | Status |
|-------|-------|--------|
| **Phase 1** | BeautifulSoup basics, HTML parsing, CSS selectors | ✅ Complete |
| **Phase 2** | Defensive parsing, error handling, timeout management | ✅ Complete |
| **Phase 3** | Pagination, multi-page crawling, URL construction | ✅ Complete |
| **Phase 4** | pandas data cleaning, normalization, deduplication | ✅ Complete |
| **Phase 5** | SQLite schema design, ORM-less CRUD, transactions | ✅ Complete |
| **Phase 6** | Performance optimization, connection pooling, indexing | 🔲 Upcoming |
| **Phase 7** | Testing, scheduling (APScheduler), CI/CD | 🔲 Upcoming |

---

## Project Structure

```
web-scraper-backend/
├── main.py                 # Entry point, orchestrates scraping → cleaning → storage
├── scraper.py              # Web scraping logic (BeautifulSoup + requests)
├── db.py                   # Database operations (queries, inserts, schema)
├── init_db.py              # Database initialization and schema creation
├── day3_sqlite.py          # SQLite learning notes and sandbox
├── json_test.py            # JSON serialization and validation tests
├── app.db                  # SQLite database (auto-created)
├── data.json               # Raw scraped data (before normalization)
├── results.json            # Cleaned, normalized data ready for export
├── requirements.txt        # Dependencies
├── .gitignore
└── README.md
```

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip

### 1. Clone & Install

```bash
git clone <repository-url>
cd web-scraper-backend
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python init_db.py
```

This creates `app.db` with the required schema (tables, indexes, constraints).

### 3. Run the Scraper

```bash
python main.py
```

**Output:**
- Scraped data → `data.json`
- Cleaned data → `results.json`
- Database → `app.db` (SQLite)

---

## Core Components

### 1. **Scraper** (`scraper.py`)

Handles HTTP requests, HTML parsing, and error recovery.

#### Key Techniques

**Defensive Parsing:**
```python
def extract_text(element, selector, default="N/A"):
    """Safely extract text with fallback."""
    try:
        el = element.select_one(selector)
        return el.get_text(strip=True) if el else default
    except AttributeError:
        return default
```

**Pagination:**
```python
def scrape_all_pages(base_url, max_pages=None):
    """Crawl multiple pages with URL parameter increments."""
    results = []
    page = 1
    while True:
        url = f"{base_url}?page={page}"
        soup = fetch_page(url)
        if not soup:
            break
        
        items = soup.select(".item")
        if not items:
            break
        
        results.extend(parse_items(items))
        page += 1
        
        if max_pages and page > max_pages:
            break
    
    return results
```

**Rate Limiting & Timeouts:**
```python
import time

def fetch_page(url, retries=3, timeout=10):
    """Fetch with exponential backoff retry."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            if attempt < retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(f"Retry {attempt + 1} after {wait}s: {e}")
                time.sleep(wait)
            else:
                print(f"Failed after {retries} attempts: {e}")
                return None
```

---

### 2. **Data Normalization** (pandas integration)

Clean, deduplicate, and validate scraped data before storage.

**Example:**
```python
import pandas as pd

def normalize_data(raw_data):
    """Convert raw scraped data to normalized DataFrame."""
    df = pd.DataFrame(raw_data)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=["id", "name"])
    
    # Type coercion
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    
    # Fill missing values
    df = df.fillna({
        "description": "N/A",
        "rating": 0
    })
    
    # Remove rows with critical nulls
    df = df.dropna(subset=["id", "name"])
    
    return df
```

---

### 3. **Database Layer** (`db.py`)

SQLite schema and CRUD operations without ORM overhead.

**Schema Example:**
```python
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    price REAL,
    description TEXT,
    rating REAL,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_product_id ON products(product_id);
CREATE INDEX idx_scraped_at ON products(scraped_at);
```

**Insertion with Transactions:**
```python
def insert_products(db_path, data):
    """Insert cleaned data with transaction rollback."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        for row in data:
            cursor.execute("""
                INSERT OR REPLACE INTO products 
                (product_id, name, price, description, rating)
                VALUES (?, ?, ?, ?, ?)
            """, (
                row["id"],
                row["name"],
                row["price"],
                row["description"],
                row["rating"]
            ))
        
        conn.commit()
        print(f"✓ Inserted {len(data)} records")
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"✗ Insertion failed: {e}")
    finally:
        conn.close()
```

**Query Examples:**
```python
def get_products_by_rating(db_path, min_rating=4.0):
    """Fetch products with minimum rating."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, price, rating
        FROM products
        WHERE rating >= ?
        ORDER BY rating DESC
    """, (min_rating,))
    
    return cursor.fetchall()
```

---

### 4. **Main Orchestration** (`main.py`)

Ties scraping, cleaning, and storage into a single pipeline.

**Typical Flow:**
```python
def main():
    print("🔄 Starting scrape pipeline...")
    
    # Step 1: Scrape
    print("📡 Scraping data...")
    raw_data = scraper.scrape_all_pages("https://example.com/products")
    
    # Save raw data for debugging
    with open("data.json", "w") as f:
        json.dump(raw_data, f, indent=2)
    
    # Step 2: Clean & normalize
    print("🧹 Normalizing data...")
    df = normalize_data(raw_data)
    
    # Step 3: Export cleaned data
    cleaned_data = df.to_dict("records")
    with open("results.json", "w") as f:
        json.dump(cleaned_data, f, indent=2)
    
    # Step 4: Persist to database
    print("💾 Writing to database...")
    insert_products("app.db", cleaned_data)
    
    print(f"✓ Complete! Processed {len(df)} records")

if __name__ == "__main__":
    main()
```

---

## Key Learnings

### Web Scraping Fundamentals
- ✅ HTML parsing with CSS selectors and defensive fallbacks
- ✅ Pagination strategies (URL params, DOM-based navigation)
- ✅ Request error handling, timeouts, and retries with exponential backoff
- ✅ User-Agent rotation and rate limiting to respect servers

### Data Pipeline Design
- ✅ Separating concerns: scraping → cleaning → storage
- ✅ pandas DataFrames for validation and normalization
- ✅ Deduplication, type coercion, and null handling
- ✅ Exporting to multiple formats (JSON, CSV, SQLite)

### Database Fundamentals
- ✅ SQLite schema design with constraints and indexes
- ✅ ACID transactions with rollback on error
- ✅ Query optimization with proper indexing
- ✅ Connection management and resource cleanup

### Production Patterns
- ✅ Logging and error recovery
- ✅ Data validation before insertion
- ✅ Atomic operations (all or nothing writes)
- ✅ Separation of raw and cleaned data (debugging aid)

---

## Usage Examples

### Run Full Pipeline

```bash
python main.py
```

Outputs:
- `data.json` — Raw, unfiltered scraped data
- `results.json` — Cleaned, normalized, deduplicated data
- `app.db` — SQLite database with searchable indexes

### Query the Database

```python
import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# Get top 10 highest-rated products
cursor.execute("""
    SELECT name, price, rating
    FROM products
    ORDER BY rating DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(row)

conn.close()
```

### Export to CSV

```python
import pandas as pd

df = pd.read_sql("SELECT * FROM products", 
                 "sqlite:///app.db")
df.to_csv("products_export.csv", index=False)
print("✓ Exported to products_export.csv")
```

---

## Testing

### Unit Tests (Recommended)

```python
# test_scraper.py
import unittest
from scraper import extract_text

class TestScraper(unittest.TestCase):
    def test_extract_text_with_element(self):
        html = '<div class="title">Hello World</div>'
        soup = BeautifulSoup(html, "html.parser")
        result = extract_text(soup, ".title")
        self.assertEqual(result, "Hello World")
    
    def test_extract_text_missing_element(self):
        html = '<div>No class here</div>'
        soup = BeautifulSoup(html, "html.parser")
        result = extract_text(soup, ".title", default="N/A")
        self.assertEqual(result, "N/A")

if __name__ == "__main__":
    unittest.main()
```

Run tests:
```bash
python -m pytest test_scraper.py -v
```

---

## Dependencies

```
beautifulsoup4==4.12.0      # HTML parsing
requests==2.31.0            # HTTP requests
pandas==2.0.0               # Data cleaning & normalization
sqlite3                     # Built-in database
lxml==4.9.0                 # Fast HTML parser (optional)
```

Install:
```bash
pip install -r requirements.txt
```

---

## Common Issues & Solutions

### 1. **Connection Timeout**
**Problem:** `requests.exceptions.ConnectTimeout`

**Solution:** Increase timeout and add retries
```python
response = requests.get(url, timeout=20)  # Increased timeout
# Use retry logic (see code examples above)
```

### 2. **Empty Results / No Data Scraped**
**Problem:** CSS selectors don't match the page

**Solution:** Inspect the page and update selectors
```bash
# Open browser DevTools (F12) and inspect the HTML structure
# Update selector in scraper.py
```

### 3. **SQLite Locked Error**
**Problem:** `sqlite3.OperationalError: database is locked`

**Solution:** Add timeout and use context managers
```python
conn = sqlite3.connect("app.db", timeout=10)
# Use try/finally to ensure conn.close() is called
```

### 4. **Duplicate Data in Database**
**Problem:** Running the scraper multiple times adds duplicates

**Solution:** Use `INSERT OR REPLACE` with unique constraints
```python
CREATE TABLE products (
    product_id TEXT UNIQUE NOT NULL,
    ...
);

INSERT OR REPLACE INTO products VALUES (...)
```

---

## Next Steps (Phases 6–7)

### Phase 6: Performance & Scalability
- Connection pooling for concurrent requests
- Database indexing strategy and query optimization
- Batch inserts for faster data loading
- Caching with Redis for API responses

### Phase 7: Production Ready
- Unit tests with pytest
- Job scheduling with APScheduler
- Docker containerization
- CI/CD pipeline (GitHub Actions)
- Monitoring and alerts
- Error notifications (email/Slack)

---

## Resources

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [pandas Getting Started](https://pandas.pydata.org/docs/getting_started/index.html)
- [SQLite Tutorial](https://www.sqlite.org/tutorial.html)
- [Web Scraping Best Practices](https://blog.apify.com/web-scraping-best-practices/)
- [Python Requests](https://requests.readthedocs.io/)

---

## License

MIT License – feel free to use this for learning and reference.

---

## Author

Built as a structured backend learning project (Phases 1–5).  
Designed to evolve through Phases 6–7 with optimization and automation.
