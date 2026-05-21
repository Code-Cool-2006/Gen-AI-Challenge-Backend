import logging
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine, Base  # Assuming you have database.py
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
from routers.market_analysis import router as market_analysis_router

# Configure logging to see server status in the terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Table Creation ---
# This function creates all the tables defined in your models.py
def create_db_and_tables():
    try:
        logger.info("Attempting to connect to the database and create tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database connection successful and tables created/verified.")
    except Exception as e:
        logger.error(f"Error connecting to the database or creating tables: {e}")

# --- Lifespan Context Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (if needed)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="CareerUp AI API",
    description="Backend services for the CareerUp platform, handling user auth, profiles, and AI-powered career tools.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS (Cross-Origin Resource Sharing) Middleware ---
# This allows your React frontend to communicate with this backend.
# IMPORTANT: For production, you should restrict this to your actual frontend domain.
origins = [
    "http://localhost:5173",  # Default Vite/React frontend address
    "http://localhost:5174",  # Vite/React frontend address (current)
    "http://localhost:5175",  # Vite/React frontend address (now)
    "http://localhost:5176",  # Vite/React frontend address (current)
    "http://localhost:3000",  # Common alternative for React dev servers
    "https://career-ai-om767.vercel.app",  # Deployed Vercel frontend URL
    # Add your deployed frontend URL here when you go live
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include All Routers ---
# This adds all the API endpoints from your different feature files to the main app.
logger.info("Including API routers...")
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(profile_routes_router)
app.include_router(career_path_routes_router)
app.include_router(interview_routes_router)
app.include_router(job_market_router)
app.include_router(review_resume_router) # Assuming you have a review_resume.py router
app.include_router(chatbot_router)
app.include_router(skill_job_matching_router)
app.include_router(job_matching_router)
app.include_router(market_analysis_router)

# Remove the incorrect alias function because APIRouter object has no such attribute.
# Instead, rely on the /market-insights route registered in market_analysis_router directly.

# The market_analysis_router is already included:
app.include_router(market_analysis_router)
logger.info("All routers included successfully.")


# --- Root Endpoint (Health Check) ---
# A simple endpoint to confirm that the server is running.
@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Welcome to the CareerUp AI Backend!"}
