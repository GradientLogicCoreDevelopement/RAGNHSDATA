import anthropic
import json
from app.core.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def decide_visualisation(question: str, results: list[dict]) -> dict:
    """
    Ask Claude to decide the best visualisation type and
    return structured data ready for the frontend to render.
    """
    if not results:
        return {"type": "narrative", "data": None}

    results_sample = results[:100]
    results_text = json.dumps(results_sample, default=str)
    columns = list(results[0].keys()) if results else []

    system_prompt = """You are a data visualisation expert working with NHS analytics data.

Given a question and query results, decide the best way to visualise the data and return a JSON object.

VISUALISATION RULES:
- bar_chart: use for comparing values across categories (e.g. rates by ICB, counts by region)
- line_chart: use for trends over time (e.g. rate changes across years)
- table: use for detailed comparisons with multiple columns, statistical significance, or when exact numbers matter most
- narrative: use when the answer is a single number, yes/no, or explanation with no meaningful chart

RESPONSE FORMAT — return ONLY valid JSON, nothing else:

For bar_chart:
{
  "type": "bar_chart",
  "title": "short descriptive title",
  "x_axis": "column name for x axis",
  "y_axis": "column name for y axis",
  "x_label": "human readable x axis label",
  "y_label": "human readable y axis label",
  "data": [{"label": "...", "value": 123.4}, ...]
}

For line_chart:
{
  "type": "line_chart",
  "title": "short descriptive title",
  "x_axis": "column name for x axis",
  "y_axis": "column name for y axis",
  "x_label": "human readable x axis label",
  "y_label": "human readable y axis label",
  "data": [{"label": "...", "value": 123.4}, ...]
}

For table:
{
  "type": "table",
  "title": "short descriptive title",
  "columns": ["col1", "col2", "col3"],
  "rows": [["val1", "val2", "val3"], ...]
}

For narrative:
{
  "type": "narrative",
  "data": null
}

IMPORTANT:
- Return ONLY the JSON object — no markdown, no backticks, no explanation
- For bar and line charts, data must be an array of {label, value} objects
- Keep titles concise — under 10 words
- For line charts x axis should always be the time dimension
- Round numeric values to 2 decimal places"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"""Question: {question}

Available columns: {columns}

Data:
{results_text}"""
        }]
    )

    raw = response.content[0].text.strip()

    # Strip accidental markdown backticks
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]

    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        # If parsing fails fall back to narrative
        return {"type": "narrative", "data": None}