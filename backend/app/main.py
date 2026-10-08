from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.soc import router as soc_router

app = FastAPI(
    title="DEEP-DECEIVER",
    description="Agentic Active-Defense Framework for securing LLMs against Prompt Injection",
    version="0.1.0"
)

# Allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)
app.include_router(soc_router)

@app.get("/")
def root():
    return {
        "message": "DEEP-DECEIVER backend is running",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }