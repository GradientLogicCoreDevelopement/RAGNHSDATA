import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import uuid

# Load embedding model once at startup (this is what converts text to numbers)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Set up ChromaDB (stores data locally in backend/data/)
chroma_client = chromadb.PersistentClient(path="./data/chromadb")


def load_file(file_path: str) -> pd.DataFrame:
    """Read a CSV or Excel file into a pandas DataFrame."""
    path = Path(file_path)
    if path.suffix == ".csv":
        return pd.read_csv(file_path)
    elif path.suffix in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def dataframe_to_chunks(df: pd.DataFrame, chunk_size: int = 50) -> list[str]:
    """
    Convert a DataFrame into text chunks.
    Each chunk is chunk_size rows converted to readable text.
    """
    chunks = []
    # Convert column names + rows into readable sentences
    for i in range(0, len(df), chunk_size):
        batch = df.iloc[i:i + chunk_size]
        chunk_text = batch.to_string(index=False)
        chunks.append(chunk_text)
    return chunks


def ingest_file(file_path: str, client_id: str) -> dict:
    """
    Full ingestion pipeline:
    1. Load file
    2. Convert to chunks
    3. Embed chunks
    4. Store in ChromaDB under client_id collection
    """
    # Each client gets their own ChromaDB collection (isolation)
    collection = chroma_client.get_or_create_collection(name=f"client_{client_id}")

    # Load and chunk
    df = load_file(file_path)
    chunks = dataframe_to_chunks(df)

    # Embed all chunks at once (faster than one at a time)
    embeddings = embedding_model.encode(chunks).tolist()

    # Store in ChromaDB
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[str(uuid.uuid4()) for _ in chunks]
    )

    return {
        "client_id": client_id,
        "file": file_path,
        "rows": len(df),
        "chunks_stored": len(chunks)
    }


def query_collection(question: str, client_id: str, n_results: int = 5) -> list[str]:
    """
    Search ChromaDB for the most relevant chunks for a given question.
    Returns top n_results chunks.
    """
    collection = chroma_client.get_or_create_collection(name=f"client_{client_id}")

    question_embedding = embedding_model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=question_embedding,
        n_results=n_results
    )

    return results["documents"][0]