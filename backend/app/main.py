from fastapi import FastAPI
from app.core.config import APP_NAME, VERSION
from app.api.routes import router

app = FastAPI(title=APP_NAME, version=VERSION)
app.include_router(router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok", "app": APP_NAME, "version": VERSION}