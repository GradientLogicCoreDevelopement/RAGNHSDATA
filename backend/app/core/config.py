from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
APP_NAME = "RAG Client App"
VERSION = "0.1.0"