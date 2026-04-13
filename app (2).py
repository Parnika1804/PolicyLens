import streamlit as st
import fitz
import json
import os
import urllib.parse
from groq import Groq

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="PolicyLens", page_icon="🔍", layout="wide")

# ─── GLOBAL STYLES (Policy Samjho inspired) ────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  /* Base */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }
  .stApp {
    background-color: #0a0f1e;
    color: #e8eaf0;
  }

  /* Hide default streamlit header/footer */
  #MainMenu, footer, header { visibility: hidden; }

  /* ── NAVBAR ── */
  .navbar {
    background: #0d1327;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1e2a4a;
    margin-bottom: 0;
  }
  .navbar-brand {
    font-size: 1.5rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
  }
  .navbar-brand span { color: #f5a623; }
  .navbar-tagline {
    font-size: 0.75rem;
    color: #8892b0;
    margin-top: 2px;
  }

  /* ── HERO SECTION ── */
  .hero {
    background: linear-gradient(135deg, #0d1327 0%, #1a2340 50%, #0d1327 100%);
    padding: 52px 40px 44px 40px;
    border-bottom: 1px solid #1e2a4a;
    text-align: center;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(245,166,35,0.12);
    color: #f5a623;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 20px;
    border: 1px solid rgba(245,166,35,0.3);
    margin-bottom: 16px;
  }
  .hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 14px;
  }
  .hero h1 span { color: #f5a623; }
  .hero-sub {
    font-size: 1.05rem;
    color: #8892b0;
    max-width: 560px;
    margin: 0 auto 24px auto;
    line-height: 1.6;
  }
  .hero-stat {
    display: inline-block;
    background: rgba(245,166,35,0.08);
    border: 1px solid rgba(245,166,35,0.2);
    border-radius: 8px;
    padding: 10px 22px;
    font-size: 0.92rem;
    color: #f5a623;
    font-weight: 500;
  }

  /* ── SECTION HEADERS ── */
  .section-header {
    padding: 32px 0 8px 0;
    border-left: 4px solid #f5a623;
    padding-left: 16px;
    margin-bottom: 4px;
  }
  .section-header h2 {
    font-size: 1.35rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 4px 0;
  }
  .section-header p {
    font-size: 0.85rem;
    color: #8892b0;
    margin: 0;
  }

  /* ── CARDS ── */
  .ps-card {
    background: #111827;
    border: 1px solid #1e2a4a;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
  }
  .ps-card:hover { border-color: #f5a623; }
  .ps-card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #f5a623;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }

  /* ── FEATURE STRIP (3 cards top) ── */
  .feature-strip {
    display: flex;
    gap: 16px;
    margin: 28px 0;
  }
  .feature-card {
    flex: 1;
    background: linear-gradient(135deg, #1a2340, #111827);
    border: 1px solid #1e2a4a;
    border-radius: 14px;
    padding: 22px 20px;
    text-align: center;
  }
  .feature-card .icon {
    font-size: 1.8rem;
    margin-bottom: 10px;
  }
  .feature-card h3 {
    font-size: 0.95rem;
    font-weight: 700;
    color: #f5a623;
    margin-bottom: 6px;
  }
  .feature-card p {
    font-size: 0.82rem;
    color: #8892b0;
    margin: 0;
    line-height: 1.5;
  }

  /* ── UPLOAD BOX ── */
  .upload-box {
    background: linear-gradient(135deg, #111827, #0d1327);
    border: 2px dashed #2a3a5e;
    border-radius: 16px;
    padding: 36px 24px;
    text-align: center;
    margin: 8px 0 24px 0;
  }
  .upload-box h3 {
    color: #ffffff;
    font-size: 1.1rem;
    margin-bottom: 6px;
  }
  .upload-box p {
    color: #8892b0;
    font-size: 0.85rem;
    margin: 0;
  }

  /* ── VERDICT BANNERS ── */
  .verdict-covered {
    background: linear-gradient(135deg, #052e16, #064e2b);
    border: 1px solid #16a34a;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 12px 0;
  }
  .verdict-not-covered {
    background: linear-gradient(135deg, #2d0a0a, #4a1010);
    border: 1px solid #dc2626;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 12px 0;
  }
  .verdict-conditional {
    background: linear-gradient(135deg, #1c1100, #2e1f00);
    border: 1px solid #d97706;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 12px 0;
  }

  /* ── SCORE CIRCLE ── */
  .score-wrap {
    text-align: center;
    padding: 24px;
    background: #111827;
    border-radius: 16px;
    border: 1px solid #1e2a4a;
  }
  .score-circle {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px auto;
    font-size: 2rem;
    font-weight: 800;
  }
  .score-good { background: radial-gradient(circle, #064e2b, #052e16); border: 3px solid #16a34a; color: #4ade80; }
  .score-ok   { background: radial-gradient(circle, #2e1f00, #1c1100); border: 3px solid #d97706; color: #fbbf24; }
  .score-bad  { background: radial-gradient(circle, #4a1010, #2d0a0a); border: 3px solid #dc2626; color: #f87171; }

  /* ── POLICY COMPARISON CARD ── */
  .policy-card {
    background: #111827;
    border: 1px solid #1e2a4a;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 14px;
  }
  .policy-card-rank {
    font-size: 1.5rem;
    margin-bottom: 6px;
  }
  .policy-card-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 2px;
  }
  .policy-card-insurer {
    font-size: 0.82rem;
    color: #f5a623;
    margin-bottom: 14px;
  }

  /* ── DIVIDER ── */
  .ps-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #1e2a4a, transparent);
    margin: 32px 0;
  }

  /* ── TIMELINE ── */
  .timeline-done {
    background: #052e16;
    border: 2px solid #16a34a;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
  }
  .timeline-upcoming {
    background: #1c1100;
    border: 2px solid #d97706;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
  }
  .timeline-target {
    background: #0c1a2e;
    border: 2px solid #3b82f6;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    box-shadow: 0 0 18px rgba(59,130,246,0.3);
  }

  /* ── STEP BADGE ── */
  .step-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(245,166,35,0.1);
    border: 1px solid rgba(245,166,35,0.3);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #f5a623;
    margin-bottom: 12px;
  }

  /* ── LINKS BOX ── */
  .links-grid {
    display: flex;
    gap: 14px;
    margin-top: 16px;
  }
  .link-card {
    flex: 1;
    background: #111827;
    border: 1px solid #1e2a4a;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
  }
  .link-card h4 { color: #f5a623; font-size: 0.88rem; margin-bottom: 4px; }
  .link-card a  { color: #60a5fa; font-size: 0.85rem; text-decoration: none; }

  /* ── FOOTER ── */
  .ps-footer {
    text-align: center;
    padding: 28px;
    border-top: 1px solid #1e2a4a;
    color: #4a5568;
    font-size: 0.82rem;
    margin-top: 48px;
  }
  .ps-footer span { color: #f5a623; }

  /* Streamlit widget overrides */
  .stButton > button {
    background: linear-gradient(135deg, #f5a623, #e09010) !important;
    color: #0a0f1e !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-size: 0.9rem !important;
    transition: opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.88 !important; }

  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div > div {
    background: #111827 !important;
    border: 1px solid #2a3a5e !important;
    border-radius: 8px !important;
    color: #e8eaf0 !important;
  }

  .stFileUploader > div {
    background: #111827 !important;
    border: 2px dashed #2a3a5e !important;
    border-radius: 12px !important;
  }

  .stExpander {
    background: #111827 !important;
    border: 1px solid #1e2a4a !important;
    border-radius: 12px !important;
  }

  .stProgress > div > div > div {
    background: linear-gradient(90deg, #f5a623, #fbbf24) !important;
    border-radius: 4px !important;
  }

  .stMetric {
    background: #111827;
    border: 1px solid #1e2a4a;
    border-radius: 12px;
    padding: 14px !important;
  }
  .stMetric label { color: #8892b0 !important; font-size: 0.8rem !important; }
  .stMetric [data-testid="metric-container"] { color: #f5a623 !important; }

  div[data-testid="stSuccess"] {
    background: #052e16 !important;
    border: 1px solid #16a34a !important;
    border-radius: 10px !important;
    color: #4ade80 !important;
  }
  div[data-testid="stError"] {
    background: #2d0a0a !important;
    border: 1px solid #dc2626 !important;
    border-radius: 10px !important;
  }
  div[data-testid="stWarning"] {
    background: #1c1100 !important;
    border: 1px solid #d97706 !important;
    border-radius: 10px !important;
  }
  div[data-testid="stInfo"] {
    background: #0c1a2e !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 10px !important;
  }
</style>
""", unsafe_allow_html=True)

# ─── NAVBAR ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div>
    <div class="navbar-brand">Policy<span>Lens</span> 🔍</div>
    <div class="navbar-tagline">Powered by AI · Built for India</div>
  </div>
  <div style="color:#8892b0;font-size:0.83rem;">India's Smartest Insurance Analyser</div>
</div>
""", unsafe_allow_html=True)

# ─── HERO ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">🔍 AI-Powered Policy Analysis</div>
  <h1>Read Your Policy in <span>Seconds.</span><br>Not 47 Pages.</h1>
  <p class="hero-sub">The average insurance policy is 47 pages of legal jargon. PolicyLens reads it instantly — giving you clarity, not confusion.</p>
  <div class="hero-stat">💡 The average insurance policy is <strong>47 pages</strong> of legal jargon. PolicyLens reads it in <strong>seconds.</strong></div>
</div>
""", unsafe_allow_html=True)

# ─── FEATURE STRIP ─────────────────────────────────────────────────────────
st.markdown("""
<div class="feature-strip">
  <div class="feature-card">
    <div class="icon">📋</div>
    <h3>Coverage Breakdown</h3>
    <p>Instant clarity on what's covered, excluded, and conditional — in plain English.</p>
  </div>
  <div class="feature-card">
    <div class="icon">🏥</div>
    <h3>Policy Health Score</h3>
    <p>Like a credit score — but for your insurance. Know how good your plan really is.</p>
  </div>
  <div class="feature-card">
    <div class="icon">⚖️</div>
    <h3>Legal Claim Guide</h3>
    <p>Claim rejected? Get step-by-step legal guidance and auto-generated appeal emails.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── UPLOAD SECTION ────────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
  <h2>📄 Upload Your Insurance Policy</h2>
  <p>Supports any PDF insurance policy — health, life, car and more</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your policy PDF", type="pdf", label_visibility="collapsed")

def extract_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

if uploaded_file:
    with st.spinner("Reading your policy..."):
        policy_text = extract_text(uploaded_file)
    st.success("✅ Policy uploaded and read successfully!")
    st.info(f"📄 Total characters read: {len(policy_text)}")

    analysis_text = policy_text

    # ─── PHASE 1 — COVERAGE BREAKDOWN ──────────────────────────────────────
    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2>📋 Phase 1 — What Does Your Policy Actually Cover?</h2>
      <p>No legal jargon. No 47 pages. Just a clean simple breakdown.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔍 Analyse My Policy"):
        with st.spinner("Analysing your policy..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a senior Indian insurance claims lawyer with 20 years of experience.
You have deep knowledge of IRDAI regulations, Insurance Act 1938, Consumer Protection Act 2019,
and all major Indian health insurance policies. Be precise, honest, and always err on the side
of caution for the policyholder."""
                    },
                    {
                        "role": "user",
                        "content": f"""You are an insurance expert.
Analyse this insurance policy and return ONLY a JSON object with exactly these 4 keys:
- covered: list of 5 things that ARE covered
- not_covered: list of 5 things that are NOT covered
- conditional: list of 5 things that are conditionally covered
- waiting_periods: list of any waiting periods mentioned

Keep each point short — max 10 words.
Return ONLY valid JSON. No extra text. No markdown.

Policy: {analysis_text[:6000]}"""
                    }
                ]
            )
            raw = response.choices[0].message.content
            try:
                clean = raw.strip().replace("```json", "").replace("```", "")
                result = json.loads(clean)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.success("✅ COVERED")
                    for item in result.get("covered", []):
                        st.write(f"• {item}")
                with col2:
                    st.error("❌ NOT COVERED")
                    for item in result.get("not_covered", []):
                        st.write(f"• {item}")
                with col3:
                    st.warning("⚠️ CONDITIONAL")
                    for item in result.get("conditional", []):
                        st.write(f"• {item}")
                with col4:
                    st.info("⏳ WAITING PERIODS")
                    for item in result.get("waiting_periods", []):
                        st.write(f"• {item}")
            except Exception as e:
                st.write(raw)

    # ─── POLICY HEALTH SCORE ────────────────────────────────────────────────
    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2>🏥 Policy Health Score</h2>
      <p>Like a credit score — but for your insurance coverage.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⚡ Generate Policy Health Score"):
        with st.spinner("Calculating your policy health score..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a senior Indian insurance claims lawyer with 20 years of experience.
You have deep knowledge of IRDAI regulations, Insurance Act 1938, Consumer Protection Act 2019,
and all major Indian health insurance policies. Be precise, honest, and always err on the side
of caution for the policyholder."""
                    },
                    {
                        "role": "user",
                        "content": f"""You are an insurance policy rating expert.

Analyse this insurance policy and return ONLY this JSON and nothing else. No markdown. No extra text:
{{
  "overall_score": 64,
  "grade": "C",
  "coverage_score": 7,
  "exclusions_score": 3,
  "waiting_period_score": 5,
  "clarity_score": 8,
  "verdict": "Your policy has too many hidden exclusions for the premium you are paying. You are underprotected.",
  "biggest_risk": "Pre-existing conditions are excluded for 4 years which is higher than industry standard."
}}

Score each out of 10. Overall score out of 100.
Grade: A (80-100), B (60-79), C (40-59), D (below 40)
Be honest and critical.

Policy: {analysis_text[:6000]}"""
                    }
                ]
            )
            raw = response.choices[0].message.content
            try:
                clean = raw.strip().replace("```json", "").replace("```", "")
                result = json.loads(clean)
                score = result.get("overall_score", 0)
                grade = result.get("grade", "N/A")

                score_cls = "score-good" if score >= 80 else ("score-ok" if score >= 60 else "score-bad")
                st.markdown(f"""
                <div class="score-wrap">
                  <div class="score-circle {score_cls}">{score}<br><span style="font-size:0.9rem">{grade}</span></div>
                  <div style="color:#e8eaf0;font-weight:700;font-size:1rem;">Policy Health Score: {score}/100</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(int(score))
                st.markdown("#### 📊 Breakdown")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("✅ Coverage", f"{result.get('coverage_score', 0)}/10")
                with col2:
                    st.metric("❌ Exclusions", f"{result.get('exclusions_score', 0)}/10")
                with col3:
                    st.metric("⏳ Waiting Periods", f"{result.get('waiting_period_score', 0)}/10")
                with col4:
                    st.metric("📋 Clarity", f"{result.get('clarity_score', 0)}/10")
                st.markdown("#### 🧠 Expert Verdict")
                verdict = result.get("verdict", "")
                if score >= 80:
                    st.success(f"💬 {verdict}")
                elif score >= 60:
                    st.warning(f"💬 {verdict}")
                else:
                    st.error(f"💬 {verdict}")
                st.markdown("#### 🚨 Biggest Risk In Your Policy")
                st.error(f"⚠️ {result.get('biggest_risk', '')}")
            except Exception as e:
                st.write(raw)

    # ─── SUGGEST BETTER POLICIES ────────────────────────────────────────────
    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2>💡 Suggest Better Policies</h2>
      <p>Based on your current policy's weaknesses — here are better alternatives in India.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("💡 Find Better Policies For Me"):
        with st.spinner("Analysing your policy and finding better alternatives..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a senior Indian insurance claims lawyer with 20 years of experience.
You have deep knowledge of IRDAI regulations, Insurance Act 1938, Consumer Protection Act 2019,
and all major Indian health insurance policies. Be precise, honest, and always err on the side
of caution for the policyholder."""
                    },
                    {
                        "role": "user",
                        "content": f"""You are an Indian insurance expert with deep knowledge of all health insurance policies available in India.

First analyse this policy and identify its weaknesses across these parameters:
- Claim settlement ratio
- Waiting period for pre-existing conditions
- Number of exclusions
- Premium vs coverage value
- Network hospitals
- No claim bonus
- Restoration benefit
- Sub-limits on room rent or ICU

Then suggest exactly 3 better real Indian health insurance policies that score higher on these parameters.

Return ONLY this JSON. No markdown. No extra text:
{{
  "current_policy_weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "better_policies": [
    {{
      "name": "Niva Bupa Reassure 2.0",
      "insurer": "Niva Bupa",
      "claim_settlement_ratio": "98.5%",
      "waiting_period": "2 years",
      "key_advantages": ["No room rent limit", "Direct claim settlement", "Unlimited restoration"],
      "approximate_premium": "₹8,000 - ₹12,000 per year",
      "trust_score": 9,
      "why_better": "Higher claim settlement ratio and fewer exclusions than your current policy"
    }},
    {{
      "name": "Policy 2 name",
      "insurer": "Insurer name",
      "claim_settlement_ratio": "XX%",
      "waiting_period": "X years",
      "key_advantages": ["advantage 1", "advantage 2", "advantage 3"],
      "approximate_premium": "₹X,XXX - ₹X,XXX per year",
      "trust_score": 8,
      "why_better": "reason"
    }},
    {{
      "name": "Policy 3 name",
      "insurer": "Insurer name",
      "claim_settlement_ratio": "XX%",
      "waiting_period": "X years",
      "key_advantages": ["advantage 1", "advantage 2", "advantage 3"],
      "approximate_premium": "₹X,XXX - ₹X,XXX per year",
      "trust_score": 7,
      "why_better": "reason"
    }}
  ]
}}

Use only real Indian health insurance policies that actually exist.
Policy: {analysis_text[:5000]}"""
                    }
                ]
            )
            raw = response.choices[0].message.content
            try:
                clean = raw.strip().replace("```json", "").replace("```", "")
                result = json.loads(clean)
                st.markdown("### ⚠️ Why Your Current Policy Is Holding You Back")
                for w in result.get("current_policy_weaknesses", []):
                    st.error(f"❌ {w}")
                st.markdown("---")
                st.markdown("### 🏆 Top 3 Better Policies For You")
                policies = result.get("better_policies", [])
                for i, policy in enumerate(policies):
                    rank = ["🥇", "🥈", "🥉"][i]
                    trust = policy.get("trust_score", 0)
                    with st.expander(f"{rank} {policy.get('name', '')} — by {policy.get('insurer', '')}", expanded=True):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Claim Settlement", policy.get("claim_settlement_ratio", "N/A"))
                        with col2:
                            st.metric("⏳ Waiting Period", policy.get("waiting_period", "N/A"))
                        with col3:
                            st.metric("💰 Premium", policy.get("approximate_premium", "N/A"))
                        with col4:
                            st.metric("⭐ Trust Score", f"{trust}/10")
                        st.markdown("**✅ Key Advantages:**")
                        for adv in policy.get("key_advantages", []):
                            st.write(f"✅ {adv}")
                        st.success(f"💬 Why it's better: {policy.get('why_better', '')}")
            except Exception as e:
                st.write(raw)
                st.error(f"Error: {e}")

    # ─── PHASE 1B — SCENARIO SIMULATOR ─────────────────────────────────────
    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2>🎯 Scenario Simulator — Will My Situation Be Covered?</h2>
      <p>Type any real life situation. We tell you if covered — and if not, exactly WHEN it will be.</p>
    </div>
    """, unsafe_allow_html=True)

    scenario = st.text_input(
        "Describe your situation in plain English",
        placeholder="e.g. My father had bypass surgery 2 years ago, can I claim for his heart attack now?"
    )

    if st.button("🔍 Check My Scenario"):
        if scenario:
            with st.spinner("Analysing your scenario..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a senior Indian insurance claims lawyer with 20 years of experience.
You have deep knowledge of IRDAI regulations, Insurance Act 1938, Consumer Protection Act 2019,
and all major Indian health insurance policies. Be precise, honest, and always err on the side
of caution for the policyholder."""
                        },
                        {
                            "role": "user",
                            "content": f"""You are an insurance claims expert.

Policy: {analysis_text[:5000]}
User situation: {scenario}
Today's date: April 2026

Analyse and return ONLY this JSON. No markdown. No extra text:
{{
  "verdict": "NOT COVERED",
  "reason": "one plain English sentence explaining why",
  "clause": "which clause applies",
  "timeline": [
    {{"date": "Jan 2025", "event": "Policy Bought", "status": "done"}},
    {{"date": "Apr 2025", "event": "Waiting Period Ends", "status": "done"}},
    {{"date": "Jan 2026", "event": "Cardiac Cover Starts", "status": "upcoming"}},
    {{"date": "Jan 2027", "event": "Pre-existing Condition Clears", "status": "target"}}
  ],
  "claim_eligible_date": "January 2027",
  "days_remaining": 365
}}

If verdict is COVERED set claim_eligible_date to TODAY and days_remaining to 0.
Always return exactly 4 timeline items.
Make dates realistic based on the policy and scenario."""
                        }
                    ]
                )
                raw = response.choices[0].message.content
                try:
                    clean = raw.strip().replace("```json", "").replace("```", "")
                    result = json.loads(clean)
                    verdict = result.get("verdict", "")
                    reason = result.get("reason", "")
                    clause = result.get("clause", "")
                    timeline = result.get("timeline", [])
                    eligible_date = result.get("claim_eligible_date", "")
                    days_remaining = result.get("days_remaining", 0)

                    if verdict == "COVERED":
                        st.success(f"✅ COVERED — You can claim right now")
                    elif verdict == "CONDITIONAL":
                        st.warning(f"⚠️ CONDITIONAL — Partially covered")
                    else:
                        st.error(f"❌ NOT COVERED TODAY — But here is your claim roadmap")

                    st.write(f"**Reason:** {reason}")
                    st.write(f"**Clause:** {clause}")
                    st.markdown("---")
                    st.subheader("📅 Your Claim Calendar")
                    if days_remaining > 0:
                        st.info(f"✅ You can claim on: **{eligible_date}** — {days_remaining} days from today")
                    else:
                        st.success(f"✅ You can claim RIGHT NOW")
                    st.markdown("---")
                    cols = st.columns(len(timeline))
                    for i, (col, item) in enumerate(zip(cols, timeline)):
                        with col:
                            status = item.get("status", "")
                            event = item.get("event", "")
                            date = item.get("date", "")
                            if status == "done":
                                st.markdown(f"""
                                <div class="timeline-done">
                                <h3 style='color:#4ade80;text-align:center;'>✅</h3>
                                <p style='color:#4ade80;font-weight:bold;text-align:center;'>{date}</p>
                                <p style='color:#e8eaf0;font-size:12px;text-align:center;'>{event}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            elif status == "upcoming":
                                st.markdown(f"""
                                <div class="timeline-upcoming">
                                <h3 style='color:#fbbf24;text-align:center;'>⏳</h3>
                                <p style='color:#fbbf24;font-weight:bold;text-align:center;'>{date}</p>
                                <p style='color:#e8eaf0;font-size:12px;text-align:center;'>{event}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            elif status == "target":
                                st.markdown(f"""
                                <div class="timeline-target">
                                <h3 style='color:#60a5fa;text-align:center;'>🎯</h3>
                                <p style='color:#60a5fa;font-weight:bold;text-align:center;'>{date}</p>
                                <p style='color:#e8eaf0;font-size:12px;text-align:center;'>{event}</p>
                                <p style='color:#60a5fa;font-size:11px;text-align:center;'>✅ CLAIM HERE</p>
                                </div>
                                """, unsafe_allow_html=True)
                    st.markdown("""
                    <div style='text-align:center; margin-top:10px;'>
                    <p style='color:#4a5568; font-size:13px;'>●────────────●────────────●────────────★</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("---")
                    st.caption("💡 PolicyLens doesn't just tell you NO — it tells you exactly WHEN the answer becomes YES.")
                except Exception as e:
                    st.write(raw)
                    st.error(f"Error: {e}")

    # ─── PHASE 2 — CLAIM REJECTION PREDICTOR ───────────────────────────────
    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2>📊 Phase 2 — Will Your Claim Be Rejected?</h2>
      <p>Enter your claim details. Our model tells you rejection risk before you file.</p>
    </div>
    """, unsafe_allow_html=True)

    claim_details = st.text_area(
        "Describe your claim",
        placeholder="e.g. Claiming for heart surgery. Patient is 55 years old. Diagnosed 3 months ago. Policy is 2 years old."
    )

    if st.button("📊 Predict Rejection Risk"):
        if claim_details:
            with st.spinner("Predicting your rejection risk..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a senior Indian insurance claims lawyer with 20 years of experience.
You have deep knowledge of IRDAI regulations, Insurance Act 1938, Consumer Protection Act 2019,
and all major Indian health insurance policies. Be precise, honest, and always err on the side
of caution for the policyholder."""
                        },
                        {
                            "role": "user",
                            "content": f"""You are an insurance claims rejection expert.

Policy: {analysis_text[:5000]}
Claim: {claim_details}

Return ONLY this JSON and nothing else. No markdown. No extra text:
{{
  "rejection_probability": 75,
  "top_reasons": ["reason 1", "reason 2", "reason 3"],
  "what_to_fix": ["fix 1", "fix 2"]
}}"""
                        }
                    ]
                )
                raw = response.choices[0].message.content
                try:
                    clean = raw.strip().replace("```json", "").replace("```", "")
                    result = json.loads(clean)
                    prob = result.get("rejection_probability", 0)
                    st.markdown("### 🎯 Rejection Risk Score")
                    if prob > 60:
                        st.error(f"🚨 High Risk — {prob}% chance of rejection")
                    elif prob > 30:
                        st.warning(f"⚠️ Medium Risk — {prob}% chance of rejection")
                    else:
                        st.success(f"✅ Low Risk — {prob}% chance of rejection")
                    st.progress(int(prob))
                    st.markdown("### ⚠️ Top Reasons Your Claim May Be Rejected")
                    for r in result.get("top_reasons", []):
                        st.write(f"❌ {r}")
                    st.markdown("### ✅ What To Fix Before Submitting")
                    for f in result.get("what_to_fix", []):
                        st.write(f"✅ {f}")
                except Exception as e:
                    st.write(raw)

    # ─── PHASE 3 — LEGAL GUIDE ──────────────────────────────────────────────
    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2>⚖️ Phase 3 — Claim Rejected? Here's Exactly What To Do Next</h2>
      <p>Step by step legal guidance in plain English. You are not helpless.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ps-card">
      <div class="ps-card-title">📝 Fill Your Details — We'll Generate Everything</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("Your Full Name", placeholder="Rahul Sharma")
        policy_number = st.text_input("Policy Number", placeholder="POL123456789")
        insurer_name = st.text_input("Insurance Company Name", placeholder="Star Health Insurance")
        insurer_email = st.text_input("Insurer Email", placeholder="grievance@starhealth.in")
    with col2:
        rejection_date = st.text_input("Date of Rejection", placeholder="10 April 2026")
        rejection_reason = st.text_input("Rejection Reason", placeholder="Pre-existing condition Clause 12")
        claim_amount = st.text_input("Claim Amount", placeholder="₹2,80,000")
        user_email = st.text_input("Your Email Address", placeholder="rahul@gmail.com")

    city = st.selectbox("Your City (for Ombudsman)", [
        "Delhi", "Mumbai", "Chennai", "Kolkata", "Bangalore",
        "Hyderabad", "Ahmedabad", "Pune", "Lucknow", "Bhopal",
        "Jaipur", "Chandigarh", "Patna", "Kochi", "Guwahati"
    ])

    ombudsman_emails = {
        "Delhi": "bimalokpal.delhi@ecoi.co.in",
        "Mumbai": "bimalokpal.mumbai@ecoi.co.in",
        "Chennai": "bimalokpal.chennai@ecoi.co.in",
        "Kolkata": "bimalokpal.kolkata@ecoi.co.in",
        "Bangalore": "bimalokpal.bengaluru@ecoi.co.in",
        "Hyderabad": "bimalokpal.hyderabad@ecoi.co.in",
        "Ahmedabad": "bimalokpal.ahmedabad@ecoi.co.in",
        "Pune": "bimalokpal.pune@ecoi.co.in",
        "Lucknow": "bimalokpal.lucknow@ecoi.co.in",
        "Bhopal": "bimalokpal.bhopal@ecoi.co.in",
        "Jaipur": "bimalokpal.jaipur@ecoi.co.in",
        "Chandigarh": "bimalokpal.chandigarh@ecoi.co.in",
        "Patna": "bimalokpal.patna@ecoi.co.in",
        "Kochi": "bimalokpal.ernakulam@ecoi.co.in",
        "Guwahati": "bimalokpal.guwahati@ecoi.co.in"
    }

    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)

    # Step 1
    st.markdown('<div class="step-badge">📨 Step 1 — Internal Appeal to Insurer (Do This on Day 1)</div>', unsafe_allow_html=True)
    with st.expander("📖 Why This Step? What To Expect?", expanded=False):
        st.markdown("""
**🔴 Why you MUST do this first:**
Before going to any authority, you must give your insurer a chance to reconsider.
If you skip this step, IRDAI and Ombudsman will reject your complaint saying you never tried internally first.

**📋 What to do:**
- Write a formal appeal to the Grievance Officer of your insurance company
- Attach: rejection letter, policy document, hospital bills, discharge summary
- Send via **email AND registered post** — keep proof of both

**⏱️ What happens next:**
- Insurer MUST reply within **15 days** by law (IRDAI Circular 2017)
- If resolved → ✅ Done
- If rejected again or no reply in 15 days → Move to Step 2 immediately

**📅 Timeline: Day 1 to Day 15**
**💰 Cost: Free**
        """)

    if st.button("⚡ Generate Internal Appeal Email"):
        if user_name and policy_number and insurer_name:
            with st.spinner("Generating legal email..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a senior Indian insurance claims lawyer with 20 years of experience.
You have deep knowledge of IRDAI regulations, Insurance Act 1938, Consumer Protection Act 2019,
and all major Indian health insurance policies."""
                        },
                        {
                            "role": "user",
                            "content": f"""Write a formal legal appeal email from a policyholder to their insurance company.
Details:
- Policyholder Name: {user_name}
- Policy Number: {policy_number}
- Insurance Company: {insurer_name}
- Rejection Date: {rejection_date}
- Rejection Reason: {rejection_reason}
- Claim Amount: {claim_amount}
Include: Formal salutation, clear dispute, Insurance Act 1938 Section 45 reference, IRDAI regulations reference, demand for reconsideration within 15 days, consequences of non-compliance.
Return ONLY the email body. No extra text."""
                        }
                    ]
                )
                email_body = response.choices[0].message.content
                subject = f"Appeal Against Claim Rejection — Policy No. {policy_number}"
                st.success("✅ Internal Appeal Email Generated")
                st.text_area("Email Preview", email_body, height=300)
                st.download_button(label="📥 Download Email", data=email_body, file_name="internal_appeal.txt", mime="text/plain")
                mailto = f"mailto:{insurer_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(email_body)}"
                st.markdown(f"[📧 Open in Email App]({mailto})")
        else:
            st.warning("Please fill Name, Policy Number and Insurer Name first")

    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)

    # Step 2
    st.markdown('<div class="step-badge">📨 Step 2 — Complaint to IRDAI (Day 15 to Day 30)</div>', unsafe_allow_html=True)
    st.caption("Send to: complaints@irdai.gov.in")
    with st.expander("📖 Why This Step? What To Expect?", expanded=False):
        st.markdown("""
**🔴 Why you need this step:**
IRDAI is the government body that regulates ALL insurance companies in India.
A complaint here puts official government pressure on your insurer.
Most insurers take IRDAI complaints very seriously and settle quickly.

**📋 What to do:**
- Go to **igms.irda.gov.in** and file online — completely free
- OR use the button below and send to complaints@irdai.gov.in
- Attach: rejection letter, your internal appeal, insurer's response or proof they didn't reply

**⏱️ What happens next:**
- IRDAI contacts your insurer within **15 days**
- Insurer must respond to IRDAI within **8 working days**
- If still unresolved after 30 days → Move to Step 3

**📅 Timeline: Day 15 to Day 45**
**💰 Cost: Free**
**✅ Success Rate: 60% of complaints resolved at this stage**
        """)

    if st.button("⚡ Generate IRDAI Complaint Email"):
        if user_name and policy_number:
            with st.spinner("Generating IRDAI complaint..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a senior Indian insurance claims lawyer with 20 years of experience.
You have deep knowledge of IRDAI regulations, Insurance Act 1938, Consumer Protection Act 2019,
and all major Indian health insurance policies."""
                        },
                        {
                            "role": "user",
                            "content": f"""Write a formal legal complaint email to IRDAI (Insurance Regulatory and Development Authority of India).
Details:
- Complainant Name: {user_name}
- Policy Number: {policy_number}
- Insurance Company: {insurer_name}
- Rejection Date: {rejection_date}
- Rejection Reason: {rejection_reason}
- Claim Amount: {claim_amount}
Include: Salutation to IRDAI Grievance Cell, unfair rejection description, IRDAI Circular 2017 reference, policyholder protection rights, request for urgent intervention and resolution within 30 days.
Return ONLY the email body. No extra text."""
                        }
                    ]
                )
                email_body = response.choices[0].message.content
                subject = f"Complaint Against {insurer_name} — Policy No. {policy_number}"
                irdai_email = "complaints@irdai.gov.in"
                st.success("✅ IRDAI Complaint Email Generated")
                st.text_area("Email Preview", email_body, height=300)
                st.download_button(label="📥 Download Email", data=email_body, file_name="irdai_complaint.txt", mime="text/plain")
                mailto = f"mailto:{irdai_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(email_body)}"
                st.markdown(f"[📧 Open in Email App — Sends to {irdai_email}]({mailto})")
        else:
            st.warning("Please fill Name and Policy Number first")

    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)

    # Step 3
    st.markdown(f'<div class="step-badge">📨 Step 3 — Complaint to Insurance Ombudsman (Day 45 to Day 90)</div>', unsafe_allow_html=True)
    st.caption(f"Your Ombudsman Office: {ombudsman_emails.get(city, '')}")
    with st.expander("📖 Why This Step? What To Expect?", expanded=False):
        st.markdown("""
**🔴 Why you need this step:**
The Insurance Ombudsman is a FREE, independent, quasi-judicial authority.
Their decision is **LEGALLY BINDING** on the insurance company.
This is your strongest weapon before going to court — and it costs nothing.

**📋 What to do:**
- Select your city above and use the button below to generate your complaint
- File at **cioins.co.in** — completely free, no lawyer needed
- Attach everything: policy, rejection letter, internal appeal, IRDAI complaint, all bills

**⏱️ What happens next:**
- Ombudsman issues notice to your insurer within **30 days**
- Decision comes within **90 days** of filing
- If decision is in your favour → insurer MUST pay within **30 days**
- Covers claims up to **₹30 lakh**

**📅 Timeline: Day 45 to Day 135**
**💰 Cost: Free**
**✅ Success Rate: 75% of cases resolved in favour of policyholder**
        """)

    if st.button("⚡ Generate Ombudsman Complaint Email"):
        if user_name and policy_number:
            with st.spinner("Generating Ombudsman complaint..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a senior Indian insurance claims lawyer with 20 years of experience.
You have deep knowledge of IRDAI regulations, Insurance Act 1938, Consumer Protection Act 2019,
and all major Indian health insurance policies."""
                        },
                        {
                            "role": "user",
                            "content": f"""Write a formal legal complaint email to the Insurance Ombudsman in India.
Details:
- Complainant Name: {user_name}
- Policy Number: {policy_number}
- Insurance Company: {insurer_name}
- Rejection Date: {rejection_date}
- Rejection Reason: {rejection_reason}
- Claim Amount: {claim_amount}
- City: {city}
Include: Salutation to Insurance Ombudsman, clear timeline of events, unfair rejection description, Insurance Ombudsman Rules 2017 reference, specific relief sought, declaration of facts.
Return ONLY the email body. No extra text."""
                        }
                    ]
                )
                email_body = response.choices[0].message.content
                ombudsman_email = ombudsman_emails.get(city, "")
                subject = f"Complaint Against {insurer_name} — Policy No. {policy_number}"
                st.success(f"✅ Ombudsman Complaint Generated — {city} Office")
                st.text_area("Email Preview", email_body, height=300)
                st.download_button(label="📥 Download Email", data=email_body, file_name="ombudsman_complaint.txt", mime="text/plain")
                mailto = f"mailto:{ombudsman_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(email_body)}"
                st.markdown(f"[📧 Open in Email App — Sends to {ombudsman_email}]({mailto})")
        else:
            st.warning("Please fill Name and Policy Number first")

    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2>📌 More Options If Above Steps Fail</h2>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📌 Step 4 — Consumer Court (Day 60 onwards)", expanded=False):
        st.markdown("""
**🔴 Why you need this step:**
Under Consumer Protection Act 2019, insurance rejection is a deficiency of service.
Courts regularly award compensation ABOVE the claim amount for mental harassment.

**📋 What to do:**
- Go to **edaakhil.nic.in** and file online
- Filing fee is only **₹200** for claims up to ₹5 lakh
- You do NOT need a lawyer — you can represent yourself

**Which court to approach:**
- Claim up to ₹50 lakh → District Consumer Forum
- Claim ₹50 lakh to ₹2 crore → State Consumer Commission
- Claim above ₹2 crore → National Consumer Commission Delhi

**📅 Timeline: Day 90 onwards**
**💰 Cost: ₹200 filing fee only**
**✅ Success Rate: 82% of insurance cases won by policyholders**
        """)

    with st.expander("📌 Step 5 — Send Legal Notice via Lawyer", expanded=False):
        st.markdown("""
**🔴 Why you need this step:**
Statistics show **80% of insurers settle** after receiving a legal notice — avoiding court entirely.

**📋 What to do:**
- Hire a local lawyer — costs between ₹500 and ₹2000 for a notice
- Lawyer sends notice via registered post to insurer's registered office
- Notice demands payment within 15 days or you will file a court case

**📅 Timeline: Can be done at ANY stage — even parallel to Step 3 or 4**
**💰 Cost: ₹500 to ₹2000**
**✅ Success Rate: 80% of cases settle after legal notice**

**💡 Pro Tip:** Send legal notice PARALLEL to Step 3 — doubles the pressure on insurer instantly.
        """)

    # ─── KEY LINKS ─────────────────────────────────────────────────────────
    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <h2>📞 Key Links</h2>
    </div>
    <div class="links-grid">
      <div class="link-card">
        <h4>IRDAI Complaint Portal</h4>
        <a href="https://igms.irda.gov.in" target="_blank">igms.irda.gov.in</a>
      </div>
      <div class="link-card">
        <h4>Insurance Ombudsman</h4>
        <a href="https://cioins.co.in" target="_blank">cioins.co.in</a>
      </div>
      <div class="link-card">
        <h4>Consumer Court</h4>
        <a href="https://edaakhil.nic.in" target="_blank">edaakhil.nic.in</a>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ps-footer">
  <span>PolicyLens</span> — Shifting the power back to the people who actually pay for it.
</div>
""", unsafe_allow_html=True)