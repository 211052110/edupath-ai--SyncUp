"""
EduPath AI — Streamlit Demo
Gap 7: Quick hackathon demo frontend.
Run: streamlit run streamlit_demo.py
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import json

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="EduPath AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 EduPath AI")
    st.markdown("*Study Abroad Intelligence for Indian Students*")
    st.divider()
    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "📊 Loan Score", "📈 ROI Calculator",
         "🎓 University Q&A", "🧠 Skill Gap Analyzer"],
        label_visibility="collapsed",
    )
    st.divider()
    backend_url = st.text_input("Backend URL", value=API_BASE)
    API_BASE = backend_url

    # Health check
    try:
        r = requests.get(API_BASE.replace("/api/v1", "") + "/health", timeout=2)
        if r.status_code == 200:
            st.success("✅ Backend connected")
        else:
            st.error("⚠ Backend error")
    except:
        st.error("❌ Backend offline")


# ── Dashboard ────────────────────────────────────────────────────────────────
if page == "🏠 Dashboard":
    st.title("🎓 EduPath AI — Study Abroad Intelligence")
    st.markdown("AI-powered platform helping Indian students make smarter study-abroad decisions.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ML Models", "2", "GBM + XGBoost")
    col2.metric("Universities", "35+", "5 Countries")
    col3.metric("RAG Chunks", "38", "FAISS indexed")
    col4.metric("Skill Categories", "8", "spaCy powered")

    st.divider()
    st.subheader("Tech Stack")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Backend**
        - FastAPI + Python 3.11
        - joblib .pkl model persistence (Gap 1)
        - XGBoost salary regressor (Gap 2)
        - FAISS + RAG University Q&A (Gap 3)
        - spaCy Skill Gap Analyzer (Gap 4)
        - LangChain ConversationChain (Gap 5)
        """)
    with col2:
        st.markdown("""
        **Infrastructure**
        - Docker + docker-compose (Gap 6)
        - Streamlit Demo (Gap 7) ← you are here
        - React + Vite + Tailwind (main UI)
        - OpenAI GPT-4o
        - scikit-learn + SHAP
        """)


# ── Loan Score ───────────────────────────────────────────────────────────────
elif page == "📊 Loan Score":
    st.title("📊 Loan Eligibility Score")
    st.markdown("ML-based (GBM + SHAP) loan scoring with lender recommendations.")

    with st.form("loan_form"):
        col1, col2 = st.columns(2)
        with col1:
            gpa = st.slider("GPA", 2.0, 4.0, 3.5, 0.1)
            budget = st.number_input("Annual Budget (USD)", 10000, 120000, 45000, 5000)
            work_exp = st.slider("Work Experience (years)", 0, 7, 1)
        with col2:
            english = st.slider("IELTS/TOEFL Score (IELTS scale)", 4.5, 9.0, 7.0, 0.5)
            country = st.selectbox("Target Country", ["USA", "Germany", "Canada", "UK", "Australia"])
            field = st.selectbox("Field of Study", ["Computer Science", "Data Science", "AI/ML", "Business", "Engineering"])
        submitted = st.form_submit_button("Calculate Loan Score", type="primary")

    if submitted:
        with st.spinner("Calculating..."):
            try:
                r = requests.post(f"{API_BASE}/loan/calculate-score", json={
                    "gpa": gpa, "annual_budget": budget,
                    "work_experience_years": work_exp, "english_score": english,
                    "target_country": country, "field_of_study": field,
                }, timeout=10)
                data = r.json()

                col1, col2, col3 = st.columns(3)
                score = data["overall_score"]
                color = "normal" if score >= 76 else "inverse"
                col1.metric("Loan Score", f"{score}/99", data["classification"])
                col2.metric("Risk Level", data["risk_level"])
                col3.metric("Classification", data["classification"])

                # Gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={"x": [0, 1], "y": [0, 1]},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#6366f1"},
                        "steps": [
                            {"range": [0, 50], "color": "#fee2e2"},
                            {"range": [50, 75], "color": "#fef9c3"},
                            {"range": [75, 100], "color": "#dcfce7"},
                        ],
                    },
                ))
                fig.update_layout(height=250, margin=dict(t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

                st.info(f"**Explanation:** {data['explanation']}")

                st.subheader("Improvement Suggestions")
                for tip in data.get("improvement_suggestions", []):
                    st.markdown(f"- {tip}")

                if data.get("recommended_lenders"):
                    st.subheader("Recommended Lenders")
                    for l in data["recommended_lenders"]:
                        with st.expander(f"🏦 {l['name']}"):
                            st.markdown(f"**Interest Rate:** {l['interest_rate']}  |  **Max Amount:** {l['max_amount']}  |  **Processing:** {l['processing_time']}")
            except Exception as e:
                st.error(f"Error: {e}")


# ── ROI Calculator ───────────────────────────────────────────────────────────
elif page == "📈 ROI Calculator":
    st.title("📈 ROI Calculator")
    st.markdown("Monte Carlo simulation + XGBoost salary prediction + World Bank live data.")

    with st.form("roi_form"):
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox("Country", ["USA", "Germany", "Canada", "UK", "Australia"])
            field = st.selectbox("Field", ["Computer Science", "Data Science", "AI/ML", "Business", "Finance"])
            gpa = st.slider("GPA", 2.5, 4.0, 3.5, 0.1)
        with col2:
            duration = st.selectbox("Program Duration (years)", [1, 2, 3])
            annual_tuition = st.number_input("Annual Tuition (USD)", 5000, 90000, 35000, 5000)
            monthly_living = st.number_input("Monthly Living Cost (USD)", 500, 4000, 1500, 100)
            work_exp = st.slider("Work Experience (years)", 0, 5, 1)
        submitted = st.form_submit_button("Calculate ROI", type="primary")

    if submitted:
        with st.spinner("Running simulation..."):
            try:
                r = requests.post(f"{API_BASE}/roi/calculate", json={
                    "target_country": country, "field_of_study": field,
                    "gpa": gpa, "program_duration_years": duration,
                    "annual_tuition_usd": annual_tuition,
                    "monthly_living_cost_usd": monthly_living,
                    "work_experience_years": work_exp,
                }, timeout=15)
                data = r.json()

                col1, col2, col3 = st.columns(3)
                col1.metric("Predicted Salary", f"${data.get('predicted_starting_salary_usd', 0):,.0f}/yr")
                col2.metric("Total Investment", f"${data.get('total_investment_usd', 0):,.0f}")
                col3.metric("10-yr ROI", f"{data.get('roi_10yr_percent', 0):.0f}%")

                if data.get("salary_projections"):
                    years = [p["year"] for p in data["salary_projections"]]
                    salaries = [p["salary"] for p in data["salary_projections"]]
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=years, y=salaries, mode="lines+markers",
                                            line=dict(color="#6366f1", width=2), name="Projected Salary"))
                    fig.update_layout(title="10-Year Salary Projection", xaxis_title="Year",
                                      yaxis_title="Salary (USD)", height=300)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")


# ── University Q&A ───────────────────────────────────────────────────────────
elif page == "🎓 University Q&A":
    st.title("🎓 University Q&A")
    st.markdown("FAISS + RAG powered Q&A. Knowledge base: 38 chunks across 5 countries + scholarships.")

    SUGGESTIONS = [
        "What are visa requirements for Germany?",
        "Compare MIT vs Stanford CS MS programs",
        "Which country has highest ROI for CS?",
        "How does UK Graduate Route visa work?",
        "What scholarships exist for Indian students?",
        "Tell me about Poonawalla Fincorp education loan",
    ]
    st.caption("Suggested questions:")
    cols = st.columns(3)
    clicked = None
    for i, s in enumerate(SUGGESTIONS):
        if cols[i % 3].button(s, key=f"sug_{i}", use_container_width=True):
            clicked = s

    question = st.text_input("Ask a question:", value=clicked or "")
    if st.button("Ask", type="primary") and question:
        with st.spinner("Searching knowledge base..."):
            try:
                r = requests.post(f"{API_BASE}/university-qa/ask",
                                  json={"question": question}, timeout=20)
                data = r.json()
                badge = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(data["confidence"], "⚪")
                st.markdown(f"**Answer** {badge} _{data['confidence']} confidence_")
                st.info(data["answer"])
                if data.get("sources"):
                    with st.expander("Sources used"):
                        for i, s in enumerate(data["sources"]):
                            st.markdown(f"{i+1}. {s}")
            except Exception as e:
                st.error(f"Error: {e}")


# ── Skill Gap ────────────────────────────────────────────────────────────────
elif page == "🧠 Skill Gap Analyzer":
    st.title("🧠 Skill Gap Analyzer")
    st.markdown("spaCy NER + keyword extraction vs role benchmarks across 5 countries.")

    ROLES = ["Data Scientist", "ML Engineer", "Software Engineer", "AI Researcher", "Data Analyst", "Full Stack Developer"]
    COUNTRIES = ["USA", "Germany", "UK", "Canada", "Australia"]

    col1, col2 = st.columns(2)
    with col1:
        role = st.selectbox("Target Role", ROLES)
    with col2:
        country = st.selectbox("Target Country", COUNTRIES)

    resume = st.text_area("Paste Resume / Skill Summary", height=200,
                          placeholder="e.g. Python, pandas, scikit-learn, 2 years ML experience, PyTorch, AWS...")
    st.caption(f"{len(resume)}/5000 characters")

    if st.button("Analyze Skills", type="primary") and resume:
        with st.spinner("Running spaCy analysis..."):
            try:
                r = requests.post(f"{API_BASE}/skill-gap/analyze", json={
                    "resume_text": resume, "target_role": role, "target_country": country,
                }, timeout=15)
                data = r.json()

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Overall Match", f"{data['overall_match']}%")
                    st.success(f"✅ **Matched:** {', '.join(data['matched_skills']) or 'None'}")
                    if data["missing_skills"]:
                        st.error(f"❌ **Gaps:** {', '.join(data['missing_skills'])}")
                    st.info(f"💡 {data['top_recommendation']}")

                with col2:
                    radar = data["radar_data"]
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=[d["user_score"] for d in radar],
                        theta=[d["skill"] for d in radar],
                        fill="toself", name="You", line_color="#6366f1",
                    ))
                    fig.add_trace(go.Scatterpolar(
                        r=[d["industry_score"] for d in radar],
                        theta=[d["skill"] for d in radar],
                        fill="toself", name="Industry", line_color="#10b981", opacity=0.5,
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(range=[0, 100])),
                        showlegend=True, height=350,
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")


# ── Career Simulator (appended) ──────────────────────────────────────────────
# Note: add "🚀 Career Simulator" to the page radio in sidebar when running standalone
