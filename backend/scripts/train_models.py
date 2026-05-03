"""
Train and persist ML models to disk.
Run once: python -m scripts.train_models

Loan model improvements:
  - SMOTE for class imbalance
  - Optuna hyperparameter tuning (50 trials)
  - LightGBM vs XGBoost — best by CV AUC saved

ROI model: XGBoost (unchanged, solid baseline)

Models saved to: backend/models/*.pkl
"""

import os
import logging
import joblib
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("train_models")

MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

LOAN_MODEL_PATH   = MODELS_DIR / "loan_gbm.pkl"
LOAN_SCALER_PATH  = MODELS_DIR / "loan_scaler.pkl"
LOAN_META_PATH    = MODELS_DIR / "loan_meta.pkl"   # stores best_model_name + cv_auc
ROI_MODEL_PATH    = MODELS_DIR / "roi_xgb.pkl"

PREMIUM_COUNTRIES = {
    "USA": 92, "Germany": 95, "Canada": 90, "Australia": 88,
    "UK": 87, "Netherlands": 85, "Singapore": 84, "New Zealand": 82,
    "Ireland": 80, "Sweden": 80,
}

SALARY_BY_COUNTRY_FIELD = {
    (0, 0): 115000, (0, 1): 112000, (0, 2): 130000, (0, 3): 85000, (0, 4): 92000,
    (1, 0):  72000, (1, 1):  70000, (1, 2):  78000, (1, 3): 58000, (1, 4): 62000,
    (2, 0):  65000, (2, 1):  64000, (2, 2):  72000, (2, 3): 55000, (2, 4): 70000,
    (3, 0):  90000, (3, 1):  88000, (3, 2): 100000, (3, 3): 70000, (3, 4): 75000,
    (4, 0):  88000, (4, 1):  86000, (4, 2):  95000, (4, 3): 72000, (4, 4): 78000,
}


# ── Data generators ───────────────────────────────────────────────────────────

def _gen_loan_data(n: int = 6000):
    """
    Synthetic loan dataset with mild class imbalance (class 0 underrepresented).
    Features: [gpa_n, budget_n, work_n, eng_n, country_risk, dti, composite_acad]
    Labels: 0=Poor, 1=Average, 2=Excellent
    """
    rng = np.random.default_rng(42)
    gpa      = rng.uniform(2.0, 4.0, n)
    budget   = rng.uniform(10000, 120000, n)
    work_exp = rng.integers(0, 8, n).astype(float)
    english  = rng.uniform(4.5, 9.0, n)
    country  = rng.choice(list(PREMIUM_COUNTRIES.values()) + [62, 58, 55], n).astype(float)

    gpa_n  = np.clip((gpa / 4.0) * 100, 0, 100)
    bud_n  = np.clip((budget / 80000) * 100, 0, 100)
    work_n = np.clip(work_exp * 14, 0, 100)
    eng_n  = np.clip((english / 9.0) * 100, 0, 100)
    dti    = budget / (budget + 30000) * 100
    comp   = (gpa_n * eng_n) / 100.0

    X = np.column_stack([gpa_n, bud_n, work_n, eng_n, country, dti, comp])
    raw = gpa_n*0.30 + bud_n*0.25 + work_n*0.20 + country*0.15 + eng_n*0.10

    # Introduce imbalance: downsample class 0 to ~12%
    y_full = np.where(raw > 75, 2, np.where(raw > 50, 1, 0))
    keep_0 = np.where(y_full == 0)[0]
    keep_0 = rng.choice(keep_0, size=int(len(keep_0) * 0.4), replace=False)
    idx = np.sort(np.concatenate([
        np.where(y_full == 1)[0],
        np.where(y_full == 2)[0],
        keep_0,
    ]))
    return X[idx], y_full[idx]


def _gen_roi_data(n: int = 5000):
    rng = np.random.default_rng(99)
    gpa      = rng.uniform(2.5, 4.0, n)
    duration = rng.integers(1, 4, n).astype(float)
    tuition  = rng.uniform(15000, 80000, n)
    living   = rng.uniform(800, 3000, n)
    country  = rng.integers(0, 5, n)
    field    = rng.integers(0, 5, n)
    work_exp = rng.integers(0, 6, n).astype(float)

    gpa_n  = (gpa / 4.0) * 100
    tui_n  = (tuition / 80000) * 100
    liv_n  = (living / 3000) * 100
    work_n = work_exp * 14
    X = np.column_stack([gpa_n, duration, tui_n, liv_n, country, field, work_n])

    base = np.array([
        SALARY_BY_COUNTRY_FIELD.get((country[i], field[i]), 70000)
        for i in range(n)
    ], dtype=float)
    gpa_boost  = ((gpa - 3.0) / 1.0) * 0.10
    work_boost = work_exp * 0.015
    noise      = rng.normal(0, 0.05, n)
    y = np.clip(base * (1 + gpa_boost + work_boost + noise), 30000, 250000)
    return X, y


# ── Loan model (SMOTE + Optuna + LightGBM vs XGBoost) ────────────────────────

def train_loan_model():
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from imblearn.over_sampling import SMOTE
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    logger.info("Generating loan data...")
    X_raw, y = _gen_loan_data()

    logger.info(f"Class distribution before SMOTE: {np.bincount(y)}")
    scaler = StandardScaler().fit(X_raw)
    X_scaled = scaler.transform(X_raw)

    # SMOTE: balance all classes
    sm = SMOTE(random_state=42, k_neighbors=5)
    X_res, y_res = sm.fit_resample(X_scaled, y)
    logger.info(f"Class distribution after SMOTE:  {np.bincount(y_res)}")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # ── Optuna: XGBoost ───────────────────────────────────────────────────────
    try:
        from xgboost import XGBClassifier
        HAS_XGB = True
    except ImportError:
        HAS_XGB = False

    xgb_auc, xgb_model = 0.0, None
    if HAS_XGB:
        logger.info("Optuna tuning XGBoost (50 trials)...")

        def xgb_objective(trial):
            params = dict(
                n_estimators    = trial.suggest_int("n_estimators", 100, 500),
                max_depth       = trial.suggest_int("max_depth", 3, 8),
                learning_rate   = trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
                subsample       = trial.suggest_float("subsample", 0.6, 1.0),
                colsample_bytree= trial.suggest_float("colsample_bytree", 0.5, 1.0),
                reg_alpha       = trial.suggest_float("reg_alpha", 1e-4, 10.0, log=True),
                reg_lambda      = trial.suggest_float("reg_lambda", 1e-4, 10.0, log=True),
                use_label_encoder= False,
                random_state     = 42,
                n_jobs           = 1,
            )
            clf = XGBClassifier(**params)
            scores = cross_val_score(clf, X_res, y_res, cv=cv,
                                     scoring="roc_auc_ovr_weighted", n_jobs=1)
            return scores.mean()

        study_xgb = optuna.create_study(direction="maximize",
                                        sampler=optuna.samplers.TPESampler(seed=42))
        study_xgb.optimize(xgb_objective, n_trials=20, show_progress_bar=False)
        best_xgb_params = study_xgb.best_params
        best_xgb_params.update({"use_label_encoder": False,
                                 "random_state": 42, "n_jobs": 1})
        xgb_model = XGBClassifier(**best_xgb_params).fit(X_res, y_res)
        xgb_auc   = study_xgb.best_value
        logger.info(f"XGBoost best CV AUC: {xgb_auc:.4f} | params: {study_xgb.best_params}")

    # ── Optuna: LightGBM ──────────────────────────────────────────────────────
    try:
        from lightgbm import LGBMClassifier
        HAS_LGB = True
    except ImportError:
        HAS_LGB = False

    lgb_auc, lgb_model = 0.0, None
    if HAS_LGB:
        logger.info("Optuna tuning LightGBM (50 trials)...")

        def lgb_objective(trial):
            params = dict(
                n_estimators    = trial.suggest_int("n_estimators", 100, 500),
                max_depth       = trial.suggest_int("max_depth", 3, 8),
                learning_rate   = trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
                num_leaves      = trial.suggest_int("num_leaves", 20, 150),
                subsample       = trial.suggest_float("subsample", 0.6, 1.0),
                colsample_bytree= trial.suggest_float("colsample_bytree", 0.5, 1.0),
                reg_alpha       = trial.suggest_float("reg_alpha", 1e-4, 10.0, log=True),
                reg_lambda      = trial.suggest_float("reg_lambda", 1e-4, 10.0, log=True),
                min_child_samples= trial.suggest_int("min_child_samples", 5, 50),
                random_state    = 42,
                n_jobs          = -1,
                verbose         = -1,
            )
            clf = LGBMClassifier(**params)
            scores = cross_val_score(clf, X_res, y_res, cv=cv,
                                     scoring="roc_auc_ovr_weighted", n_jobs=1)
            return scores.mean()

        study_lgb = optuna.create_study(direction="maximize",
                                        sampler=optuna.samplers.TPESampler(seed=42))
        study_lgb.optimize(lgb_objective, n_trials=20, show_progress_bar=False)
        best_lgb_params = study_lgb.best_params
        best_lgb_params.update({"random_state": 42, "n_jobs": -1, "verbose": -1})
        lgb_model = LGBMClassifier(**best_lgb_params).fit(X_res, y_res)
        lgb_auc   = study_lgb.best_value
        logger.info(f"LightGBM best CV AUC: {lgb_auc:.4f} | params: {study_lgb.best_params}")

    # ── Fallback: sklearn GBM ─────────────────────────────────────────────────
    if not HAS_XGB and not HAS_LGB:
        logger.warning("Neither XGBoost nor LightGBM found — falling back to GradientBoostingClassifier")
        from sklearn.ensemble import GradientBoostingClassifier
        fallback = GradientBoostingClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            subsample=0.8, random_state=42,
        ).fit(X_res, y_res)
        joblib.dump(fallback, LOAN_MODEL_PATH, compress=3)
        joblib.dump(scaler,   LOAN_SCALER_PATH, compress=3)
        joblib.dump({"best_model": "GBM_fallback", "cv_auc": None}, LOAN_META_PATH, compress=3)
        logger.info("Fallback GBM saved.")
        return fallback, scaler

    # ── Pick winner ───────────────────────────────────────────────────────────
    if xgb_auc >= lgb_auc:
        best_model      = xgb_model
        best_model_name = "XGBoost"
        best_auc        = xgb_auc
    else:
        best_model      = lgb_model
        best_model_name = "LightGBM"
        best_auc        = lgb_auc

    logger.info(f"Winner: {best_model_name} (AUC {best_auc:.4f})")

    joblib.dump(best_model, LOAN_MODEL_PATH,  compress=3)
    joblib.dump(scaler,     LOAN_SCALER_PATH, compress=3)
    joblib.dump({
        "best_model":  best_model_name,
        "cv_auc":      best_auc,
        "xgb_auc":     xgb_auc if HAS_XGB else None,
        "lgb_auc":     lgb_auc if HAS_LGB else None,
    }, LOAN_META_PATH, compress=3)

    logger.info(f"Saved → {LOAN_MODEL_PATH.name}, {LOAN_SCALER_PATH.name}, {LOAN_META_PATH.name}")
    return best_model, scaler


# ── ROI model (XGBoost, unchanged) ───────────────────────────────────────────

def train_roi_model():
    try:
        from xgboost import XGBRegressor
        HAS_XGB = True
    except ImportError:
        from sklearn.ensemble import GradientBoostingRegressor
        HAS_XGB = False

    logger.info(f"Training ROI {'XGBoost' if HAS_XGB else 'GBR'} salary regressor...")
    X, y = _gen_roi_data()

    if HAS_XGB:
        model = XGBRegressor(
            n_estimators=400, max_depth=5, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            reg_alpha=0.1, reg_lambda=1.0,
            random_state=42, n_jobs=-1,
        ).fit(X, y)
    else:
        from sklearn.ensemble import GradientBoostingRegressor
        model = GradientBoostingRegressor(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            subsample=0.8, random_state=42,
        ).fit(X, y)

    joblib.dump(model, ROI_MODEL_PATH, compress=3)
    logger.info(f"Saved → {ROI_MODEL_PATH.name}")
    return model


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    train_loan_model()
    train_roi_model()

    # Print model comparison summary
    if LOAN_META_PATH.exists():
        meta = joblib.load(LOAN_META_PATH)
        print("\n── Loan Model Training Summary ──────────────────")
        print(f"  Winner:       {meta['best_model']}")
        print(f"  Best CV AUC:  {meta['cv_auc']:.4f}" if meta['cv_auc'] else "")
        if meta.get('xgb_auc'):
            print(f"  XGBoost AUC:  {meta['xgb_auc']:.4f}")
        if meta.get('lgb_auc'):
            print(f"  LightGBM AUC: {meta['lgb_auc']:.4f}")
        print("─────────────────────────────────────────────────\n")

    print("All models saved to backend/models/")
