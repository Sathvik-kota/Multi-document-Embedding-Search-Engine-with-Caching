import streamlit as st
import requests
import json
import html
import sys
import os
import importlib

# ------------------------------------------
# Add project root + eval folder to path
# ------------------------------------------
CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)

sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "eval"))

# ------------------------------------------
# FORCE RELOAD evaluate module
# ------------------------------------------
import eval.evaluate as eval_module
importlib.reload(eval_module)
from eval.evaluate import run_evaluation


API_GATEWAY_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Doc-Fetch",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =======================
# GEMINI UI STYLING
# =======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
        color: #1f1f1f;
    }

    /* Input Field Fix */
    .stTextInput > div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 24px !important; 
        box-shadow: none !important; 
    }
    .stTextInput input {
        border-radius: 24px !important;
        background-color: #f0f4f9 !important;
        border: 1px solid transparent !important;
        color: #1f1f1f !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        transition: all 0.2s ease;
    }
    .stTextInput input:focus {
        background-color: #ffffff !important;
        border-color: #0b57d0 !important;
        box-shadow: 0 0 0 2px rgba(11, 87, 208, 0.2) !important;
        outline: none !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 20px;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
        white-space: nowrap;
        min-width: 140px;
    }
    button[kind="primary"] {
        background: linear-gradient(90deg, #4b90ff, #ff5546);
        color: white;
    }
    button[kind="primary"]:hover {
        opacity: 0.9;
        box-shadow: 0 4px 12px rgba(75, 144, 255, 0.3);
    }

    /* Result Cards */
    .result-card {
        background-color: #f0f4f9;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .result-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* Gradient Header */
    .gradient-text {
        background: linear-gradient(to right, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
    }
</style>
""", unsafe_allow_html=True)


# =======================
# SIDEBAR
# =======================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    top_k = st.slider("Top-K Results", 1, 10, 5)
    url_input = st.text_input("API Endpoint", API_GATEWAY_URL)
    st.divider()
    st.subheader(" Evaluation")
    run_eval = st.button("Run Evaluation Script")
    st.divider()
    st.caption("Semantic Search · Smart Cache · FAISS Retrieval · Multi-Service Architecture · MiniLM Embeddings · LLM Reasoning.")

API_GATEWAY_URL = url_input


# =======================
# MAIN HEADER
# =======================
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown('<div style="text-align: center; margin-bottom: 10px;"><span class="gradient-text">Hello, Explorer</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #444746; font-size: 1.2rem; margin-bottom: 30px;">How can I help you find documents today?</div>', unsafe_allow_html=True)


# =======================
# SEARCH BAR
# =======================
sc1, sc2, sc3 = st.columns([1, 4, 1])

# =======================
# DISABLE AUTOCOMPLETE (YOUR PATCH)
# =======================
st.markdown("""
<style>
input[type=text] { autocomplete: off !important; }
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const inputs = window.parent.document.querySelectorAll('input[type="text"]');
    inputs.forEach(inp => {
        inp.setAttribute('autocomplete', 'off');
        inp.setAttribute('autocorrect', 'off');
        inp.setAttribute('autocapitalize', 'off');
        inp.setAttribute('spellcheck', 'false');
    });
});
</script>
""", unsafe_allow_html=True)

with sc2:
    query = st.text_input(
        "Search Query",
        placeholder="Ask a question about your documents...",
        label_visibility="collapsed"
    )

    b1, b2, b3 = st.columns([2, 1, 2])
    with b2:
        submit_btn = st.button("Sparkle Search", type="primary", use_container_width=True)


# =======================
# SEARCH HANDLER
# =======================
if submit_btn and query.strip():

    with st.spinner("✨ Analyzing semantics..."):

        response = requests.post(
            f"{API_GATEWAY_URL}/search",
            json={"query": query, "top_k": top_k}
        )

        if response.status_code != 200:
            st.error(f"❌ Connection Error: {response.text}")
            st.stop()

        data = response.json()

    if "results" not in data:
        st.info("No relevant documents found.")
        st.stop()

    st.markdown("### ✨ Search Results")
    st.markdown("---")

    # ---------------------
    # RESULT CARDS
    # ---------------------
    for item in data["results"]:
        filename = item["filename"]
        score = item["score"]
        explanation = item["explanation"]
        preview = item["preview"]
        full_text = item["full_text"]

        safe_preview = html.escape(preview)

        keywords = explanation.get("keyword_overlap", [])
        keyword_html = "".join([f"<span class='keyword-pill'>{kw}</span>" for kw in keywords])

        st.markdown(f"""
        <div class="result-card">
            <div style="display:flex; justify-content:space-between;">
                <div class="card-title">
                    📄 {filename}
                </div>
                <div class="score-badge">match: {score:.4f}</div>
            </div>
            <p class="card-preview">{safe_preview}...</p>
            <div>{keyword_html}</div>
        </div>
        """, unsafe_allow_html=True)

        # ---- DETAILS EXPANDER ----
        with st.expander(f"View Document Insights: Semantic Overlap, Top Sentences, LLM Reasoning & Full Text for {filename}"):

            overlap_ratio = explanation.get("overlap_ratio", 0)
            sentences = explanation.get("top_sentences", [])

            st.caption(f"Semantic Overlap Ratio: {overlap_ratio:.3f}")

            if sentences:
                st.markdown("**Key Excerpts:**")
                for s in sentences:
                    st.markdown(f"""
                    <div style='background:#fff; border-left:3px solid #4285f4; padding:10px; margin-bottom:5px;'>
                        "{s['sentence']}" 
                        <span style='font-size:0.8em; color:#555;'> (conf: {s['score']:.2f})</span>
                    </div>
                    """, unsafe_allow_html=True)

            llm_expl = explanation.get("llm_explanation")
            if llm_expl:
                st.markdown("**Why this document?**")
                st.write(llm_expl)

            st.markdown("---")
            st.markdown("**📄 Full Document Content:**")
            st.code(full_text, language="text")


# =======================
# EVALUATION SECTION
# =======================
if run_eval:

    st.info("Running evaluation...")

    results = run_evaluation(top_k=10)

    st.success("Evaluation Complete!")

    st.markdown("## Evaluation Summary")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Accuracy", f"{results['accuracy']}%")
    with c2: st.metric("MRR", results["mrr"])
    with c3: st.metric("NDCG", results["ndcg"])
    with c4: st.metric("Queries", results["total_queries"])

    st.markdown("---")

    wrong = [d for d in results["details"] if not d["is_correct"]]
    st.markdown("## Incorrect Fetches")

    if wrong:
        for item in wrong:
            st.markdown(f"""
            <div style="padding:14px; background:#ffe5e5;
                        border-left:5px solid #ff4d4f;
                        border-radius:8px; margin-bottom:10px;">
                <b>Query:</b> {item['query']}<br>
                <b>Expected:</b> {item['expected']}<br>
                <b>Retrieved:</b> {item['retrieved']}<br>
                <b>Rank:</b> {item['rank']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No incorrect queries!")

    st.markdown("---")

    st.markdown("## Correct Fetches")
    correct_items = [d for d in results["details"] if d["is_correct"]]

    if correct_items:
        for item in correct_items:
            st.markdown(f"""
            <div style="padding:14px; background:#e8ffe5;
                        border-left:5px solid #2ecc71;
                        border-radius:8px; margin-bottom:10px;">
                <b>Query:</b> {item['query']}<br>
                <b>Expected:</b> {item['expected']}<br>
                <b>Top-K Retrieved:</b> {item['retrieved']}<br>
                <b>Rank:</b> {item['rank']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No correct queries.")

    st.markdown("---")

    st.markdown("## Full Evaluation Table")
    table_data = [
        {
            "Query": d["query"],
            "Expected Doc": d["expected"],
            "Retrieved (Top-10)": ", ".join(d["retrieved"]),
            "Correct?": "Yes" if d["is_correct"] else "No",
            "Rank": d["rank"],
        }
        for d in results["details"]
    ]

    st.dataframe(table_data, use_container_width=True)
