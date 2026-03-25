import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DB_PATH = "./data/readmissions.db"
TABLE_NAME = "readmissions"


def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}")


def ingest_file(file_path: str, client_id: str) -> dict:
    """
    Load CSV into SQLite database.
    Replaces the ChromaDB ingestion approach.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read CSV
    df = pd.read_csv(file_path)

    # Clean column names — strip whitespace just in case
    df.columns = df.columns.str.strip()
    df.columns = (df.columns
    .str.replace('%', 'pct', regex=False)
    .str.replace('.', '_', regex=False)
    .str.strip()
    )

    # Write to SQLite — replace table if it exists
    engine = get_engine()
    df.to_sql(TABLE_NAME, engine, if_exists="replace", index=False)

    # Verify it loaded
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).scalar()

    logger.info(f"Ingested {count} rows into SQLite table '{TABLE_NAME}'")

    return {
        "client_id": client_id,
        "file": file_path,
        "rows_loaded": count,
        "table": TABLE_NAME,
        "database": DB_PATH
    }


def run_sql(query: str) -> list[dict]:
    """
    Execute a SQL query against the SQLite database.
    Returns results as a list of dicts.
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]


def get_sample_values(column: str, limit: int = 20) -> list:
    """
    Get sample distinct values from a column.
    Useful for Claude to understand what values exist.
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT DISTINCT {column} FROM {TABLE_NAME} LIMIT {limit}")
        )
        return [row[0] for row in result.fetchall()]