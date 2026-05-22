import logging
import time
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine, Base
from utils.security import general_limiter, get_client_ip


# ── Routers ──────────────────────────────────────────────────
from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.profile_routes import router as profile_routes_router
from routers.career_path_routes import router as career_path_routes_router

from routers.interview_routes import router as interview_routes_router
from routers.job_market import router as job_market_router
from routers.review_resume import router as review_resume_router
from routers.chatbot import router as chatbot_router
from routers.skill_job_matching import router as skill_job_matching_router
from routers.job_matching import router as job_matching_router




# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ── DB Setup ──────────────────────────────────────────────────
def create_db_and_tables():
    try:
        logger.info("Connecting to database and creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database ready.")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")


# ── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    logger.info("🚀 CareerBridge AI Backend started")
    yield
    logger.info("🛑 CareerBridge AI Backend stopped")


# ── App Init ──────────────────────────────────────────────────
app = FastAPI(
    title="CareerBridge AI API",
    description="Multi-portal backend — Students, Institutions, Companies & Startups.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)


# ── CORS ──────────────────────────────────────────────────────
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Rate-Limit-Remaining"],
)


# ── Security Middleware ────────────────────────────────────────
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    client_ip = get_client_ip(request)
    start_time = time.time()

    # Global rate limit: 200 req/min per IP
    if general_limiter.is_rate_limited(client_ip, max_requests=200, window_seconds=60):
        logger.warning(f"🚫 Rate limit exceeded: {client_ip}")
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})

    response = await call_next(request)

    # Security headers
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response


# ── Routers ───────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(profile_routes_router)
app.include_router(career_path_routes_router)
app.include_router(interview_routes_router)
app.include_router(job_market_router)
app.include_router(review_resume_router)
app.include_router(chatbot_router)
app.include_router(skill_job_matching_router)
app.include_router(job_matching_router)

logger.info("✅ All routers loaded.")


# ── Global Error Handler ──────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."}
    )


# ── Health Checks ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"message": "CareerBridge AI Backend v2.0.0", "status": "healthy"}


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok", "timestamp": time.time(), "version": "2.0.0"}
