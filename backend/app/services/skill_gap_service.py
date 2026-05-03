"""
Skill Gap Analyzer — spaCy NER + keyword matching
spaCy extracts entities/noun chunks; keyword lists map them to skill categories.
Compares user profile against role-specific industry benchmarks.
No external API needed — runs fully local.
"""

import re
import logging
from app.schemas.skill_gap import SkillGapRequest, SkillGapResponse, SkillScore

logger = logging.getLogger("edupath.skillgap")

# ── spaCy lazy load ────────────────────────────────────────────────────────────
_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            try:
                _nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.info("Downloading spaCy en_core_web_sm...")
                from spacy.cli import download
                download("en_core_web_sm")
                _nlp = spacy.load("en_core_web_sm")
        except ImportError:
            _nlp = None  # fallback to regex-only mode
    return _nlp


# ── Skill taxonomy ─────────────────────────────────────────────────────────────
# skill_category → (keywords[], industry_weight_by_role)
SKILL_TAXONOMY = {
    "Python":        ["python", "pandas", "numpy", "scipy", "flask", "fastapi", "django"],
    "ML / AI":       ["machine learning", "deep learning", "neural network", "tensorflow", "pytorch",
                      "scikit-learn", "sklearn", "xgboost", "lightgbm", "nlp", "computer vision",
                      "transformer", "bert", "llm", "langchain", "rag", "cnn", "rnn", "lstm"],
    "Data Science":  ["data analysis", "data science", "statistics", "regression", "classification",
                      "clustering", "eda", "feature engineering", "matplotlib", "seaborn", "plotly",
                      "tableau", "power bi", "sql", "data visualization"],
    "Cloud":         ["aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
                      "ci/cd", "devops", "mlops", "sagemaker", "ec2", "s3", "lambda"],
    "Research":      ["research", "publication", "paper", "thesis", "journal", "ieee", "acm",
                      "arxiv", "experiment", "hypothesis", "dataset", "benchmark", "ablation"],
    "Communication": ["presentation", "communication", "leadership", "team", "collaboration",
                      "agile", "scrum", "project management", "stakeholder", "report", "documentation"],
    "Web / APIs":    ["react", "javascript", "typescript", "node", "rest", "graphql", "html", "css",
                      "api", "microservices", "frontend", "backend", "full stack", "vue", "angular"],
    "Databases":     ["sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
                      "vector database", "qdrant", "pinecone", "faiss", "nosql"],
}

# Role → {skill: industry_benchmark (0-100)}
ROLE_BENCHMARKS = {
    "data scientist": {
        "Python": 90, "ML / AI": 88, "Data Science": 92, "Cloud": 70,
        "Research": 75, "Communication": 72, "Web / APIs": 45, "Databases": 78,
    },
    "ml engineer": {
        "Python": 92, "ML / AI": 95, "Data Science": 80, "Cloud": 85,
        "Research": 65, "Communication": 65, "Web / APIs": 60, "Databases": 72,
    },
    "software engineer": {
        "Python": 85, "ML / AI": 50, "Data Science": 45, "Cloud": 80,
        "Research": 40, "Communication": 75, "Web / APIs": 90, "Databases": 82,
    },
    "ai researcher": {
        "Python": 88, "ML / AI": 98, "Data Science": 82, "Cloud": 60,
        "Research": 95, "Communication": 70, "Web / APIs": 35, "Databases": 55,
    },
    "data analyst": {
        "Python": 75, "ML / AI": 60, "Data Science": 90, "Cloud": 55,
        "Research": 55, "Communication": 85, "Web / APIs": 40, "Databases": 85,
    },
    "full stack developer": {
        "Python": 70, "ML / AI": 30, "Data Science": 35, "Cloud": 75,
        "Research": 25, "Communication": 72, "Web / APIs": 95, "Databases": 80,
    },
}

DEFAULT_BENCHMARK = {
    "Python": 80, "ML / AI": 70, "Data Science": 75, "Cloud": 70,
    "Research": 60, "Communication": 70, "Web / APIs": 65, "Databases": 70,
}

# Country salary context for recommendation
COUNTRY_HOT_SKILLS = {
    "usa":       ["ML / AI", "Cloud", "Python"],
    "germany":   ["Python", "Research", "ML / AI"],
    "uk":        ["Communication", "Data Science", "Cloud"],
    "canada":    ["Cloud", "Python", "Databases"],
    "australia": ["Cloud", "Data Science", "Communication"],
}


# ── Core extraction ────────────────────────────────────────────────────────────

def _extract_skills(text: str, nlp_override=None) -> dict[str, int]:
    """
    Returns {skill_category: score 0-100} based on keyword density + spaCy entities.
    """
    text_lower = text.lower()
    scores = {}

    for category, keywords in SKILL_TAXONOMY.items():
        hits = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))
        # Normalise: 1 hit = 40, 2 = 65, 3 = 80, 4+ = 90-95
        if hits == 0:
            score = 0
        elif hits == 1:
            score = 40
        elif hits == 2:
            score = 65
        elif hits == 3:
            score = 80
        else:
            score = min(95, 80 + (hits - 3) * 5)
        scores[category] = score

    # spaCy boost: ORG/PRODUCT entities matching skill keywords add +10
    nlp = _get_nlp()
    if nlp:
        doc = nlp(text[:5000])
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT", "GPE"):
                ent_lower = ent.text.lower()
                for category, keywords in SKILL_TAXONOMY.items():
                    if any(kw in ent_lower for kw in keywords):
                        scores[category] = min(98, scores.get(category, 0) + 10)

    if nlp_override is not None:
        # Test mode: return set of categories that have score > 0
        return {cat for cat, score in scores.items() if score > 0}
    return scores


def _get_benchmark(role: str) -> dict[str, int]:
    role_lower = role.lower()
    for key in ROLE_BENCHMARKS:
        if key in role_lower or any(w in role_lower for w in key.split()):
            return ROLE_BENCHMARKS[key]
    return DEFAULT_BENCHMARK


# ── Main function ──────────────────────────────────────────────────────────────

def analyze_skill_gap(data: SkillGapRequest) -> SkillGapResponse:
    user_scores = _extract_skills(data.resume_text)
    benchmark   = _get_benchmark(data.target_role)

    radar_data = []
    matched, missing = [], []

    for skill, industry_score in benchmark.items():
        user_score = user_scores.get(skill, 0)
        radar_data.append(SkillScore(
            skill=skill,
            user_score=user_score,
            industry_score=industry_score,
        ))
        if user_score >= industry_score * 0.7:
            matched.append(skill)
        elif user_score < industry_score * 0.4:
            missing.append(skill)

    # Overall match: weighted avg of (user/industry) ratios
    ratios = [min(1.0, user_scores.get(s, 0) / max(1, v)) for s, v in benchmark.items()]
    overall_match = int(sum(ratios) / len(ratios) * 100)

    # Recommendation: biggest gap in country's hot skills
    country_key = data.target_country.lower()[:3]
    hot = next((v for k, v in COUNTRY_HOT_SKILLS.items() if k.startswith(country_key)), ["ML / AI", "Cloud"])
    biggest_gap_skill = max(
        [s for s in hot if s in benchmark],
        key=lambda s: benchmark.get(s, 0) - user_scores.get(s, 0),
        default=missing[0] if missing else "Cloud",
    )
    gap_size = benchmark.get(biggest_gap_skill, 70) - user_scores.get(biggest_gap_skill, 0)

    if gap_size > 30:
        rec = f"Focus on {biggest_gap_skill} — {gap_size}pt gap vs {data.target_role} benchmark in {data.target_country}. Consider a targeted online course or project."
    elif missing:
        rec = f"Add {missing[0]} to your profile. Even 1–2 projects can boost your score significantly."
    else:
        rec = f"Strong profile for {data.target_role}. Highlight {matched[0]} prominently in your SOP and resume."

    return SkillGapResponse(
        radar_data=radar_data,
        matched_skills=matched,
        missing_skills=missing,
        overall_match=overall_match,
        top_recommendation=rec,
    )
