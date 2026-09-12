# Personal Budget API

A simple REST API for recording income and expenses, filtering transactions, and calculating a budget summary. Built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- Add income and expense transactions.
- Filter transactions by type and date range.
- View total income, total expenses, and the remaining balance.
- Store data persistently in PostgreSQL.
- Validate request data using Pydantic.
- Create the transactions table automatically on startup.
- Try the endpoints using Swagger UI.

## Project Files

| File | Purpose |
| --- | --- |
| `main.py` | API endpoints, date filtering, and budget calculations |
| `models.py` | SQLAlchemy transaction model |
| `schemas.py` | Request validation and response schemas |
| `database.py` | Database engine, sessions, and database error handling |
| `config.py` | Reads database settings from `.env` |
| `.env.example` | Example database configuration |
| `.gitignore` | Excludes local environment files and Python cache files from Git |
| `requirements.txt` | Python dependencies |

## Requirements

- Python 3.12 or newer (64-bit)
- A running PostgreSQL server

## Setup

Run the following commands from the project directory containing `main.py`.

### 1. Create a virtual environment and install dependencies

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

### 2. Create the database

Create a database named `budget_db` using pgAdmin, or run this SQL command while connected to an existing database such as `postgres`:

```sql
CREATE DATABASE budget_db;
```

Skip this step if the database already exists. The application creates the `transactions` table automatically when it starts. Existing records are preserved. Automatic table creation does not update the structure of an existing table.

### 3. Configure the database connection

Copy `.env.example` to `.env`.

Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

If you already have a configured `.env`, keep it instead of overwriting it. Edit its values to match your PostgreSQL setup:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=budget_db
DB_USER=postgres
DB_PASSWORD="YOUR_POSTGRES_PASSWORD"
```

Replace `YOUR_POSTGRES_PASSWORD` with your actual password. Keep `.env` local and publish only the placeholder values in `.env.example`.

### 4. Start the API

Windows (PowerShell):

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

macOS / Linux:

```bash
./.venv/bin/python -m uvicorn main:app --reload
```

Open [Swagger UI](http://127.0.0.1:8000/docs) in your browser. Select an endpoint, click **Try it out**, enter the request data, and click **Execute**.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/transactions/` | Add an income or expense transaction |
| GET | `/transactions/` | List transactions with optional filters |
| GET | `/budget/summary` | Get total income, total expenses, and balance |

### Add a transaction

Send this JSON body to `POST /transactions/`:

```json
{
  "amount": 1000,
  "type": "income",
  "category": "Salary",
  "created_at": "2026-09-01T10:00:00Z"
}
```

For an expense:

```json
{
  "amount": 150,
  "type": "expense",
  "category": "Food",
  "created_at": "2026-09-12T12:00:00Z"
}
```

A successful request returns **201 Created**, including the generated transaction ID. Each POST request adds a new record.

- `amount` must be a positive JSON number with at most two decimal places, up to `9999999999.99`. Expenses also use positive amounts.
- `type` must be `income` or `expense`.
- `category` must contain 1–100 characters after trimming whitespace.
- `created_at` is optional. If omitted, the current UTC time is used. If supplied, it must include a timezone, for example `Z` or `+04:00`.

### Filter transactions

Example request:

```text
GET /transactions/?type=expense&start_date=2026-09-01&end_date=2026-09-12
```

| Parameter | Required | Format |
| --- | --- | --- |
| `type` | No | `income` or `expense` |
| `start_date` | No | `YYYY-MM-DD` |
| `end_date` | No | `YYYY-MM-DD` |

Filters can be used separately or together. Both boundary days are included, using UTC. Results are ordered from newest to oldest. Omit all filters to list every transaction.

Invalid filter dates return **400 Bad Request** with the field name, expected format, and an example. For example:

```json
{
  "detail": "start_date: Tarixi YYYY-MM-DD formatında yazın. Məsələn: 2026-09-12. Tarix mövcud gün olmalıdır."
}
```

This means: “Enter the date in YYYY-MM-DD format, for example 2026-09-12. The date must be a valid calendar day.” Application error messages are in Azerbaijani.

Values such as `12.09.2026`, `2026-9-1`, and `2026-02-30` are rejected. The start date must not be later than the end date.

### Get the budget summary

```text
GET /budget/summary
```

If the database contains only the two example transactions above, the response is:

```json
{
  "total_income": "1000.00",
  "total_expense": "150.00",
  "balance": "850.00"
}
```

Balance is calculated as total income minus total expenses. The summary includes all transactions, independently of the list filters. An empty database returns zero totals.

Amounts use Python `Decimal` and PostgreSQL `Numeric(12, 2)`. Decimal values are returned as JSON strings to preserve their decimal representation; request amounts must be JSON numbers.

## Error Handling

| Situation | HTTP status |
| --- | --- |
| Invalid, zero, or negative amount | 422 |
| Invalid transaction type or missing required fields | 422 |
| Empty category or invalid `created_at` | 422 |
| Invalid `start_date` or `end_date` | 400 |
| Start date later than end date | 400 |
| Database operation failure during a request | 503 |

Failed database operations are rolled back, and database sessions are closed after requests. If PostgreSQL is unavailable at startup, the application stops with a configuration error message. Check the database service and `.env` settings, then restart it.

## Scope and Verification

This is a single-user learning project. It does not include authentication, transaction editing, or deletion. All amounts are assumed to use the same currency.

The summary uses a simple Python loop for readability. For large datasets, calculating totals directly in the database would be more efficient.

During development, endpoint checks passed against a temporary SQLite test database, including transaction creation, filtering, totals, and invalid inputs. Additional checks covered the date-format error messages. PostgreSQL table SQL generation was also checked. Live PostgreSQL connectivity and manual Swagger testing should be verified locally using the setup above. The application itself is configured for PostgreSQL.
