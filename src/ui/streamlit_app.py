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
    initial_sidebar_state="expanded"
)

# =======================
# Disable Autocomplete
# =======================
st.markdown("""
<style>
input[type=text] {
    autocomplete: off !important;
}
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

# =======================
# GEMINI UI STYLING
# =======================
st.markdown("""
<style>
/* Your entire CSS EXACTLY as earlier (not reprinting for brevity) */
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
    st.caption("Semantic Search · Smart Cache · FAISS Retrieval · Multi-Service Architecture · Relevance by MiniLM Embeddings · Reasoning by LLM.")

API_GATEWAY_URL = url_input

# =======================
# MAIN HEADER
# =======================
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown('<div style="text-align:center;margin-bottom:10px;"><span class="gradient-text">Hello, Explorer</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;color:#444746;font-size:1.2rem;margin-bottom:30px;">How can I help you find documents today?</div>', unsafe_allow_html=True)


# =======================
# SEARCH INPUT (ENTER TRIGGER)
# =======================

# SESSION STATE to detect Enter key automatically
if "trigger_enter" not in st.session_state:
    st.session_state["trigger_enter"] = False

def enter_pressed():
    st.session_state["trigger_enter"] = True

sc1, sc2, sc3 = st.columns([1,4,1])

with sc2:
    query = st.text_input(
        "Search Query",
        placeholder="Ask a question about your documents...",
        label_visibility="collapsed",
        key="search_box",
        on_change=enter_pressed  # <-- ENTER activates search
    )

    # Buttons row
    b1, b2, b3 = st.columns([2,1,2])
    with b2:
        submit_btn = st.button("Sparkle Search", type="primary", use_container_width=True)

# TRUE if button clicked OR Enter pressed
trigger_search = submit_btn or st.session_state["trigger_enter"]

# =======================
# SEARCH HANDLER
# =======================
if trigger_search and query.strip():

    # Reset enter state
    st.session_state["trigger_enter"] = False

    with st.spinner("✨ Analyzing semantics..."):
        response = requests.post(
            f"{API_GATEWAY_URL}/search",
            json={"query": query, "top_k": top_k}
        )

        if response.status_code != 200:
            st.error(f"❌ Connection Error: {response.text}")
            st.stop()

        try:
            data = response.json()
        except:
            st.error("❌ Invalid JSON response.")
            st.stop()

    if "results" not in data:
        st.info("No relevant documents found for that query.")
        st.stop()

    # Search Results
    st.markdown("### ✨ Search Results")
    st.markdown("---")

    for item in data["results"]:
        filename = item["filename"]
        score = item["score"]
        explanation = item["explanation"]
        preview = item["preview"]
        full_text = item["full_text"]

        safe_preview = html.escape(preview)
        
        keywords = explanation.get("keyword_overlap", [])
        keyword_html = "".join([f"<span class='keyword-pill'>{kw}</span>" for kw in keywords])

        doc_icon = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0b57d0" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>"""

        st.markdown(f"""
        <div class="result-card">
            <div style="display:flex;justify-content:space-between;align-items:start;">
                <div class="card-title">{doc_icon} {filename}</div>
                <div class="score-badge">match: {score:.4f}</div>
            </div>
            <p class="card-preview">{safe_preview}...</p>
            <div style="margin-top:10px;">
                <div style="font-weight:600;color:#1f1f1f;margin-bottom:6px;">Keyword Overlap:</div>
                {keyword_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"View Document Insights: Semantic Overlap, Top Sentences, LLM Reasoning & Full Text for {filename}"):
            overlap_ratio = explanation.get("overlap_ratio", 0)
            sentences = explanation.get("top_sentences", [])
            
            st.caption(f"Semantic Overlap Ratio: {overlap_ratio:.3f}")

            if sentences:
                st.markdown("**Key Excerpts:**")
                for s in sentences:
                    st.markdown(f"""
                    <div style="background:#fff;border-left:3px solid #4285f4;padding:10px;margin-bottom:5px;border-radius:0 8px 8px 0;">
                        "{s['sentence']}" <span style="color:#5e5e5e;font-size:0.8em;">(conf: {s['score']:.2f})</span>
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
# EVALUATION MODULE
# =======================
if run_eval:

    st.info("Running evaluation... this may take 10–20 seconds...")
    results = run_evaluation(top_k=10)
    st.success("Evaluation Complete!")

    st.markdown("## Evaluation Summary")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Accuracy", f"{results['accuracy']}%")
    with c2: st.metric("MRR", results["mrr"])
    with c3: st.metric("NDCG", results["ndcg"])
    with c4: st.metric("Queries", results["total_queries"])

    st.markdown(
        f"**Correct:** {results['correct_count']} | **Incorrect:** {results['incorrect_count']}"
    )

    st.markdown("---")
