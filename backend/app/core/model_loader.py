"""
Central model loader.
Loads .pkl files from backend/models/.
If missing, trains and saves them automatically (first boot).
"""

import logging
import joblib
import numpy as np
from pathlib import Path

logger = logging.getLogger("edupath.models")

MODELS_DIR = Path(__file__).parent.parent.parent / "models"

LOAN_MODEL_PATH  = MODELS_DIR / "loan_gbm.pkl"
LOAN_SCALER_PATH = MODELS_DIR / "loan_scaler.pkl"
LOAN_META_PATH   = MODELS_DIR / "loan_meta.pkl"
ROI_MODEL_PATH   = MODELS_DIR / "roi_xgb.pkl"

# In-process cache
_loan_model  = None
_loan_scaler = None
_loan_meta   = None
_roi_model   = None


def _ensure_models():
    missing = not (LOAN_MODEL_PATH.exists() and LOAN_SCALER_PATH.exists() and ROI_MODEL_PATH.exists())
    if missing:
        logger.info("Model files missing — training now (one-time ~60s with Optuna)...")
        MODELS_DIR.mkdir(exist_ok=True)
        from scripts.train_models import train_loan_model, train_roi_model
        train_loan_model()
        train_roi_model()


def get_loan_model():
    global _loan_model, _loan_scaler
    if _loan_model is None:
        _ensure_models()
        logger.info("Loading loan model from disk...")
        _loan_model  = joblib.load(LOAN_MODEL_PATH)
        _loan_scaler = joblib.load(LOAN_SCALER_PATH)
    return _loan_model, _loan_scaler


def get_loan_meta() -> dict:
    """Returns training metadata: best_model name, cv_auc, comparison."""
    global _loan_meta
    if _loan_meta is None:
        if LOAN_META_PATH.exists():
            _loan_meta = joblib.load(LOAN_META_PATH)
        else:
            _loan_meta = {}
    return _loan_meta


def get_roi_model():
    global _roi_model
    if _roi_model is None:
        _ensure_models()
        logger.info("Loading ROI model from disk...")
        _roi_model = joblib.load(ROI_MODEL_PATH)
    return _roi_model
