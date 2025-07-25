## Overview

Financial-Scraping is a Python tool for asynchronously scraping financial articles from sites like `ft.com`, storing them in a PostgreSQL database, and serving them via a FastAPI endpoint. It uses `httpx` for HTTP requests, `BeautifulSoup` for parsing, `Pydantic` for data validation, and Celery for task queuing, making it efficient for large-scale data collection.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/g1Den1s-it/Financial-Scraping.git
   cd Financial-Scraping
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file:
   ```bash
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=financial_db
   ```

5. **Run Docker compose**
   ```bash
   docker compose build
   docker compose up
   ```

6. **Run Migrations**
   ```bash
   alembic upgrade head
   ```
