import anthropic
import json
from pathlib import Path
from app.core.config import ANTHROPIC_API_KEY
from app.services.ingestion import run_sql, get_sample_values, TABLE_NAME

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SCHEMA_PATH = "./data/schema_description.md"


def load_schema() -> str:
    """Load the schema description from file."""
    path = Path(SCHEMA_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")
    return path.read_text(encoding="utf-8")


def get_dimension_samples() -> str:
    """
    Fetch sample values for key categorical columns.
    This helps Claude write accurate WHERE clauses.
    """
    try:
        samples = {
            "dimension_type": get_sample_values("dimension_type"),
            "age_breakdown": get_sample_values("age_breakdown"),
            "sex_breakdown": get_sample_values("sex_breakdown"),
            "year": get_sample_values("year"),
            "data_frequency": get_sample_values("data_frequency"),
        }
        lines = ["Sample values in key columns (use these exactly in WHERE clauses):"]
        for col, vals in samples.items():
            lines.append(f"  {col}: {vals}")
        return "\n".join(lines)
    except Exception as e:
        return f"Could not load sample values: {str(e)}"


def generate_sql(question: str, schema: str, samples: str) -> str:
    """
    Ask Claude to write a SQL query for the question.
    Returns only the SQL string.
    """
    system_prompt = f"""You are an expert SQL analyst working with an NHS readmissions dataset in SQLite.

The table name is: {TABLE_NAME}

{schema}

{samples}

RULES:
- Return ONLY the SQL query, nothing else — no explanation, no markdown, no backticks
- Always filter age_breakdown = 'All' and sex_breakdown = 'All' unless the question specifically asks for a breakdown by age or sex
- Always filter data_frequency = 'Annual' unless the question asks for a specific time period
- Never use SUM() on indirectly_standardised_percentage_rate — use AVG(), MAX() or MIN() instead
- For readmission counts use the numerator column
- For rates use indirectly_standardised_percentage_rate
- Use LIKE for text searches on dimension_description (e.g. WHERE dimension_description LIKE '%Manchester%')
- Always include dimension_description in SELECT when filtering by dimension
- Limit results to 20 rows unless the question asks for more
- If comparing ICB and CCG periods, include a comment in the query noting the non-alignment warning"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": question}]
    )

    sql = response.content[0].text.strip()

    # Strip any accidental markdown backticks
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[1]
    if sql.endswith("```"):
        sql = sql.rsplit("```", 1)[0]

    return sql.strip()


def narrate_results(question: str, sql: str, results: list[dict]) -> str:
    """
    Ask Claude to turn raw SQL results into a clear narrative answer.
    """
    if not results:
        return "The query returned no results. This may mean the data doesn't exist for the filters applied, or the question needs rephrasing."

    # Limit results sent to Claude to avoid token overuse
    results_sample = results[:50]
    results_text = json.dumps(results_sample, indent=2, default=str)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system="""You are an NHS data analyst assistant. 
You have run a SQL query and received results from a readmissions dataset.
Write a clear, concise narrative answer to the user's question based on the data.
- Lead with the most important finding
- Use specific numbers from the data
- Note any important caveats (e.g. ICB/CCG alignment issues if present)
- If the results are a ranked list, highlight the top 3-5 items
- Keep it professional but readable — this is for NHS managers and analysts""",
        messages=[{
            "role": "user",
            "content": f"""Question: {question}

SQL used:
{sql}

Results:
{results_text}

{'Note: Results truncated to 50 rows for summary.' if len(results) > 50 else ''}"""
        }]
    )

    return response.content[0].text


def ask(question: str, client_id: str, file_path: str = None) -> dict:
    """
    Full text-to-SQL pipeline:
    1. Load schema description
    2. Get sample values for key columns
    3. Ask Claude to write SQL
    4. Run SQL against SQLite
    5. Ask Claude to narrate the results
    """
    # Load schema
    schema = load_schema()

    # Get sample values to help Claude write accurate queries
    samples = get_dimension_samples()

    # Generate SQL
    sql = generate_sql(question, schema, samples)

    # Run the query
    try:
        results = run_sql(sql)
    except Exception as e:
        # If SQL fails, return the error with the generated SQL for debugging
        return {
            "question": question,
            "sql_generated": sql,
            "error": str(e),
            "answer": f"The query failed to execute. Generated SQL was:\n{sql}\n\nError: {str(e)}"
        }

    # Narrate results
    answer = narrate_results(question, sql, results)

    return {
        "question": question,
        "sql_generated": sql,
        "rows_returned": len(results),
        "answer": answer
    }