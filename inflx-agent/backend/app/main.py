import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.leads import router as leads_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AutoStream AI Agent backend...")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="AutoStream AI Agent",
    description="LangGraph-powered sales agent with RAG, intent classification, and lead capture",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(leads_router, prefix="/api", tags=["Leads"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "inflx-autostream-agent"}
