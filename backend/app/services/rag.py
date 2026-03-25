import anthropic
from app.core.config import ANTHROPIC_API_KEY
from app.services.ingestion import query_collection

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def ask(question: str, client_id: str) -> dict:
    """
    Full RAG pipeline:
    1. Find relevant chunks from ChromaDB
    2. Build a prompt with those chunks as context
    3. Send to Claude and return the answer
    """

    # Step 1 — retrieve relevant chunks
    chunks = query_collection(question, client_id)
    context = "\n\n---\n\n".join(chunks)

    # Step 2 — build the prompt
    system_prompt = """You are a data analyst assistant. 
You are given context extracted from a client's dataset.
Answer the user's question using only the provided context.
Be specific, cite numbers where possible, and be concise.
If the context doesn't contain enough information to answer, say so clearly."""

    user_prompt = f"""Context from the dataset:
{context}

Question: {question}"""

    # Step 3 — call Claude
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        system=system_prompt
    )

    return {
        "question": question,
        "answer": message.content[0].text,
        "chunks_used": len(chunks)
    }