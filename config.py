import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL


load_dotenv(Path(__file__).with_name(".env"))

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "budget_db"),
)
