"""
RAG University Q&A — FAISS + LangChain + Groq (free)
Embeddings: sentence-transformers (local, free — no API needed)
LLM: llama-3.3-70b-versatile via Groq
"""

import logging
from app.core.config import settings

logger = logging.getLogger("edupath.rag")

UNIVERSITY_DOCS = [
    "MIT CS MS tuition ~$60,000/year. Cambridge MA. Acceptance rate ~4%. Requires GRE, TOEFL 100+/IELTS 7.5+. F-1 visa. Strong AI/ML labs. OPT 3-year STEM extension available.",
    "Stanford CS MS tuition ~$62,000/year. Stanford CA. Acceptance rate ~6%. Top AI/ML program. TOEFL 100+/IELTS 7.0+. OPT 3-year STEM extension after graduation.",
    "Carnegie Mellon MSCS tuition ~$58,000/year. Pittsburgh PA. Known for AI, robotics, software engineering. TOEFL 100+ or IELTS 7.5+.",
    "UT Austin MSCS tuition ~$20,000/year for international students. High ROI. Requires GRE and TOEFL 79+ or IELTS 6.5+.",
    "Georgia Tech MSCS online (OMS) ~$7,000 total. On-campus ~$32,000/year. Atlanta GA. Highest ROI CS program in USA.",
    "University of Washington MSCS tuition ~$35,000/year. Seattle WA. Strong industry links with Amazon, Microsoft, Boeing.",
    "USA F-1 student visa requires: I-20 form from university, SEVIS fee $350, DS-160 application, visa interview, proof of funds covering first year tuition + living costs.",
    "USA OPT (Optional Practical Training): 12 months work authorization after graduation. STEM fields get 24-month extension (total 36 months). Must apply 90 days before graduation.",
    "TU Munich MS programs tuition-free for international students (~€150 semester fee). Munich. English-taught CS and AI programs. Blocked account €11,208 required for German student visa.",
    "RWTH Aachen MS Computer Science and Data Science in English. No tuition (~€300 semester fee). Strong engineering reputation. Located in Aachen near Dutch/Belgian border.",
    "Germany student visa requires: university admission letter, blocked account €11,208 at Deutsche Bank/Fintiba/Expatrio, health insurance, valid passport, IELTS 6.5+/TOEFL 90+ or German B2.",
    "Germany post-study work visa: 18-month job-seeker visa after graduation. Average CS salary in Germany: €45,000–€72,000/year. Berlin and Munich are top tech hubs.",
    "University of Edinburgh MSc CS tuition ~£32,000/year international. 1-year program. Edinburgh Scotland. Strong AI research group.",
    "Imperial College London MSc Computing tuition ~£38,000/year. London. 1-year intensive. Strong industry links. QS World Rank top 10.",
    "UK Student Visa requires: CAS number from university, IELTS 6.5+ overall, proof of funds £1,334/month London or £1,023/month outside London for 9 months, TB test for Indian applicants.",
    "UK Graduate Route visa: 2-year post-study work visa (3 years for PhD). Any job/skill level allowed. CS starting salaries in London: £45,000–£65,000.",
    "University of Toronto MScAC (Applied Computing) tuition ~CAD 32,000/year. 1-year professional master's. Toronto. Strong co-op placement with Canadian tech firms.",
    "UBC Master of Data Science tuition ~CAD 28,000 total. Vancouver. 10-month program. High employment rate.",
    "Canada Study Permit requires: acceptance letter, proof of funds CAD 10,000+ per year beyond tuition, valid passport, biometrics. Processing 4–12 weeks.",
    "Canada Post-Graduation Work Permit (PGWP): up to 3 years for 2+ year programs. Pathway to Express Entry PR. Average CS salary Toronto: CAD 85,000–120,000.",
    "University of Melbourne Master of CS tuition ~AUD 44,000/year. 2-year program. Melbourne. Strong research output. QS top 35 globally.",
    "Australian Student Visa (Subclass 500) requires: CoE from university, IELTS 6.5+/TOEFL 79+, Genuine Temporary Entrant (GTE) statement, funds AUD 21,041/year + tuition.",
    "Australia Post-Study Work Visa (Subclass 485): 2–4 years depending on degree and study location. CS median salary Sydney: AUD 95,000–130,000.",
    "Fulbright-Nehru Fellowship: Indian students to USA. Covers tuition, living stipend, health insurance. Deadline July each year.",
    "DAAD Scholarship Germany: full scholarship for Indian students including tuition waiver + €934/month stipend + travel. Apply by October for following year.",
    "Chevening Scholarship UK: full funding for 1-year master's. Covers tuition + living + flights. Requires 2 years work experience. Deadline November.",
    "Erasmus Mundus Joint Masters: EU-funded scholarships for international students. Cover tuition + €1,400/month stipend. Programs in AI, CS, data science.",
    "Poonawalla Fincorp Education Loan: study in USA, UK, Canada, Germany, Australia. Up to ₹50 lakh (~$60,000). Interest 10.99%–13.00%. No collateral required. Processing 3–5 days.",
    "SBI Global Ed-Vantage up to ₹1.5 Cr at 10.90%. HDFC Credila up to ₹75L at 11.25–13.50%. Avanse up to ₹1Cr. Prodigy Finance for top-ranked universities without collateral.",
    "Average ROI for international CS degree: USA 580% over 10 years, Germany 820% (low tuition + high salary), Canada 510%, Australia 490%, UK 470%. Germany highest ROI due to near-zero tuition.",
    "Break-even analysis: USA CS degree breaks even in ~2.5 years post-graduation. Germany in ~1 year. UK in ~2 years.",
]

_vectorstore = None


def _build_vectorstore():
    """FAISS index using local HuggingFace embeddings — no API key needed."""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.schema import Document

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    docs = [Document(page_content=chunk, metadata={"index": i})
            for i, chunk in enumerate(UNIVERSITY_DOCS)]
    return FAISS.from_documents(docs, embeddings)


def _get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        logger.info("Building FAISS index (local embeddings, no API needed)...")
        _vectorstore = _build_vectorstore()
        logger.info(f"FAISS index built: {len(UNIVERSITY_DOCS)} chunks")
    return _vectorstore


def answer_university_question(question: str) -> dict:
    from groq import Groq

    key = settings.GROQ_API_KEY.strip()
    if not key or key.startswith("gsk_your"):
        return {"answer": "Groq API key not configured. Set GROQ_API_KEY in backend/.env (get free key at console.groq.com) then restart backend.", "sources": [], "confidence": "low"}

    try:
        vs = _get_vectorstore()
        results = vs.similarity_search_with_score(question, k=4)
    except Exception as e:
        logger.error(f"FAISS retrieval error: {e}")
        return {"answer": "Knowledge base unavailable.", "sources": [], "confidence": "low"}

    threshold = 1.5
    relevant = [(doc, score) for doc, score in results if score < threshold]

    if not relevant:
        return {
            "answer": "I don't have specific information on that. Try asking about tuition, visa requirements, scholarships, or loan options for USA, UK, Germany, Canada, or Australia.",
            "sources": [], "confidence": "low",
        }

    context = "\n\n".join(f"[{i+1}] {doc.page_content}" for i, (doc, _) in enumerate(relevant))
    avg_score = sum(s for _, s in relevant) / len(relevant)
    confidence = "high" if avg_score < 0.6 else "medium" if avg_score < 1.1 else "low"

    prompt = f"""You are an expert advisor for Indian students planning to study abroad.
Answer ONLY using the provided context. Be specific and concise (3-5 sentences max).

Context:
{context}

Question: {question}

Answer:"""

    try:
        client = Groq(api_key=key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
        )
        answer = resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq error: {e}")
        answer = relevant[0][0].page_content  # fallback

    sources = [doc.page_content[:80] + "..." for doc, _ in relevant]
    return {"answer": answer, "sources": sources, "confidence": confidence}
