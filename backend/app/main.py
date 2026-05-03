import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import loan, roi, chat, university_qa, skill_gap, career_sim, cache

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("edupath")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm models on startup (trains if missing ~60s first boot)
    logger.info("Startup: pre-warming ML models...")
    try:
        from app.core.model_loader import get_loan_model, get_roi_model
        get_loan_model()
        get_roi_model()
        logger.info("Models ready.")
    except Exception as e:
        logger.warning(f"Model pre-warm failed (will retry on first request): {e}")
    yield
    logger.info("Shutdown.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins if settings.ENV == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loan.router,          prefix=f"{settings.API_V1_STR}/loan",          tags=["Loan Scoring"])
app.include_router(roi.router,           prefix=f"{settings.API_V1_STR}/roi",           tags=["ROI Calculator"])
app.include_router(career_sim.router,    prefix=f"{settings.API_V1_STR}/career-sim",    tags=["Career Simulator"])
app.include_router(skill_gap.router,     prefix=f"{settings.API_V1_STR}/skill-gap",     tags=["Skill Gap"])
app.include_router(university_qa.router, prefix=f"{settings.API_V1_STR}/university-qa", tags=["University Q&A"])
app.include_router(chat.router,          prefix=f"{settings.API_V1_STR}/chat",          tags=["Visa Chat"])
app.include_router(cache.router,         prefix=f"{settings.API_V1_STR}/cache",         tags=["Cache"])


@app.get("/health")
def health_check():
    from app.core.cache import cache_info
    key_set = bool(settings.GROQ_API_KEY and not settings.GROQ_API_KEY.startswith("gsk_your"))
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "env": settings.ENV,
        "groq_key_configured": key_set,
        "cache": cache_info(),
    }
