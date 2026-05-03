"""
Lender catalogue — structured for easy API replacement.

Each entry mirrors a real Indian/global education loan product (May 2026).
To connect a real lender API:
  1. Add api_endpoint + api_key to the entry
  2. Replace LenderRecommendation with live fetch in loan_service.py
"""

LENDER_CATALOGUE = [
    {
        "min_score": 55,
        "name": "SBI Global Ed-Vantage",
        "interest_rate": "10.90%",
        "max_amount": "₹1.5 Cr (~$180k)",
        "processing_time": "15-20 days",
        "collateral_required": True,
        "countries": ["USA", "UK", "Canada", "Australia", "Germany", "Singapore"],
        "api_endpoint": None,  # placeholder: "https://api.sbi.co.in/edu-loan/check"
        "apply_url": "https://sbi.co.in/web/personal-banking/loans/education-loans/sbi-global-ed-vantage-scheme",
    },
    {
        "min_score": 58,
        "name": "Bank of Baroda Baroda Scholar",
        "interest_rate": "10.85%",
        "max_amount": "₹1.5 Cr (~$180k)",
        "processing_time": "10-15 days",
        "collateral_required": True,
        "countries": ["USA", "UK", "Canada", "Australia", "Germany"],
        "api_endpoint": None,
        "apply_url": "https://www.bankofbaroda.in/personal-banking/loans/education-loan/baroda-scholar",
    },
    {
        "min_score": 62,
        "name": "HDFC Credila",
        "interest_rate": "11.25–13.50%",
        "max_amount": "₹75 L (~$90k)",
        "processing_time": "7-10 days",
        "collateral_required": False,
        "countries": ["USA", "UK", "Canada", "Australia", "Germany", "Netherlands", "Ireland"],
        "api_endpoint": None,  # placeholder: "https://api.hdfccredila.com/v1/eligibility"
        "apply_url": "https://www.hdfccredila.com",
    },
    {
        "min_score": 65,
        "name": "Poonawalla Fincorp Education Loan",
        "interest_rate": "10.99–13.00%",
        "max_amount": "₹50 L (~$60k)",
        "processing_time": "3-5 days",
        "collateral_required": False,
        "countries": ["USA", "UK", "Canada", "Australia", "Germany"],
        "api_endpoint": None,
        "apply_url": "https://www.poonawallafincorp.com/education-loan",
    },
    {
        "min_score": 70,
        "name": "Avanse Financial Services",
        "interest_rate": "11.00–13.50%",
        "max_amount": "₹1 Cr (~$120k)",
        "processing_time": "4-7 days",
        "collateral_required": False,
        "countries": ["USA", "UK", "Canada", "Australia", "Germany", "Singapore", "Ireland"],
        "api_endpoint": None,
        "apply_url": "https://www.avanse.com",
    },
    {
        "min_score": 75,
        "name": "InCred Education Loan",
        "interest_rate": "11.50–14.00%",
        "max_amount": "₹1 Cr (~$120k)",
        "processing_time": "3-5 days",
        "collateral_required": False,
        "countries": ["USA", "UK", "Canada", "Australia", "Germany"],
        "api_endpoint": None,
        "apply_url": "https://www.incred.com/education-loan",
    },
    {
        "min_score": 82,
        "name": "Prodigy Finance",
        "interest_rate": "9.99–13.00%",
        "max_amount": "$220k",
        "processing_time": "2-4 days",
        "collateral_required": False,
        "countries": ["USA", "UK", "Canada", "Australia", "Germany", "Netherlands", "Sweden", "Ireland"],
        "api_endpoint": None,  # placeholder: "https://api.prodigyfinance.com/v2/pre-qualify"
        "apply_url": "https://prodigyfinance.com",
    },
    {
        "min_score": 88,
        "name": "MPOWER Financing",
        "interest_rate": "12.99–14.98%",
        "max_amount": "$100k",
        "processing_time": "2-3 days",
        "collateral_required": False,
        "countries": ["USA", "Canada"],
        "api_endpoint": None,  # placeholder: "https://api.mpowerfinancing.com/apply"
        "apply_url": "https://www.mpowerfinancing.com",
    },
]


def get_lenders_for(score: int, country: str) -> list[dict]:
    """
    Filter lenders by score threshold AND country support.
    Returns top 4 most relevant (highest threshold first).
    """
    matched = [
        l for l in LENDER_CATALOGUE
        if score >= l["min_score"] and (
            not l["countries"] or
            any(c.lower() in country.lower() for c in l["countries"])
        )
    ]
    # Sort by min_score descending (most exclusive first), cap at 4
    matched.sort(key=lambda x: x["min_score"], reverse=True)
    return matched[:4]
