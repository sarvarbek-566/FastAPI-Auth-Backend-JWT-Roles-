from fastapi import FastAPI
from app.api.routers.auth import router as auth_router
from app.core.db import Base, engine

app = FastAPI(title="Auth API", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok"}
