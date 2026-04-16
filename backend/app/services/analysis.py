import anthropic
import json
from app.core.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def narrate_and_visualise(question: str, sql: str, results: list[dict]) -> dict:
    """
    Single Claude call that returns both:
    - A narrative answer to the question
    - Structured visualisation data for the frontend
    Replaces the previous two separate calls.
    """
    if not results:
        return {
            "answer": "The query returned no results. This may mean the data doesn't exist for the filters applied, or the question needs rephrasing.",
            "visualisation": {"type": "narrative", "data": None}
        }

    results_sample = results[:50]
    results_text = json.dumps(results_sample, indent=2, default=str)
    columns = list(results[0].keys()) if results else []

    system_prompt = """You are an NHS data analyst assistant with expertise in data visualisation.

                        Given a question and SQL query results, return a JSON object with exactly two keys: "answer" and "visualisation".

                        ANSWER RULES:
                        - Write a clear, concise narrative answering the question
                        - Lead with the most important finding
                        - Use specific numbers from the data
                        - Note any important caveats (e.g. ICB/CCG alignment issues)
                        - If results are a ranked list, highlight the top 3-5 items
                        - Keep it professional but readable for NHS managers and analysts
                        - Use markdown formatting — bold key numbers, use bullet points for lists

                        VISUALISATION RULES — choose the best type:
                        - bar_chart: comparing values across categories (rates by ICB, counts by region)
                        - line_chart: trends over time (rate changes across years)
                        - table: detailed comparisons with multiple columns, statistical significance
                        - narrative: single number answers, yes/no questions, explanations with no meaningful chart

                        RESPONSE FORMAT — return ONLY this JSON, no markdown, no backticks:
                        {
                        "answer": "your narrative text here with **bold** markdown",
                        "visualisation": {
                            "type": "bar_chart",
                            "title": "short descriptive title under 10 words",
                            "x_label": "human readable x axis label",
                            "y_label": "human readable y axis label",
                            "data": [{"label": "...", "value": 123.4}, ...]
                        }
                        }

                        For table type use:
                        {
                        "answer": "narrative text",
                        "visualisation": {
                            "type": "table",
                            "title": "short title",
                            "columns": ["col1", "col2"],
                            "rows": [["val1", "val2"], ...]
                        }
                        }

                        For narrative type use:
                        {
                        "answer": "narrative text",
                        "visualisation": {"type": "narrative", "data": null}
                        }

                        IMPORTANT:
                        - Return ONLY the JSON object
                        - Round numeric values to 2 decimal places
                        - For bar and line charts, data must be array of {label, value} objects
                        - Keep titles concise"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"""Question: {question}
            SQL used:{sql}

            Available columns: {columns}

            Results: {results_text}
            {'Note: Results truncated to 50 rows.' if len(results) > 50 else ''}"""
        }]
    )

    raw = response.content[0].text.strip()

    # Strip accidental markdown backticks
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]

    try:
        parsed = json.loads(raw.strip())
        return {
            "answer": parsed.get("answer", "No answer returned."),
            "visualisation": parsed.get("visualisation", {"type": "narrative", "data": None})
        }
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "answer": raw,
            "visualisation": {"type": "narrative", "data": None}
        }