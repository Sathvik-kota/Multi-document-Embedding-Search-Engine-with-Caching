import streamlit as st
import requests
import json
import re

# ===========================================
# CONFIG
# ===========================================
API_GATEWAY_URL = "http://localhost:8000"   # change to HF Space URL later

st.set_page_config(
    page_title="Multi-Document Search Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===========================================
# STYLING
# ===========================================
st.markdown("""
<style>
.result-card {
    padding: 1rem;
    border-radius: 10px;
    background-color: #1e1e1e;
    margin-bottom: 1.2rem;
    border: 1px solid #333333;
}
.score-badge {
    background-color: #4CAF50;
    padding: 4px 10px;
    border-radius: 5px;
    color: white;
    font-size: 0.8rem;
}
.keyword {
    background-color: #ffcc00;
    color: black;
    padding: 2px 4px;
    border-radius: 4px;
    margin-right: 3px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ===========================================
# HEADER
# ===========================================
st.title("🔍 Multi-Document Embedding Search Engine")
st.subheader("Fast. Explainable. Semantic Search over 150 Newsgroup Docs.")

st.markdown("---")

# ===========================================
# SIDEBAR
# ===========================================
with st.sidebar:
    st.header("⚙️ Settings")
    top_k = st.slider("Top-K Results", 1, 10, 5)
    st.markdown("### 🔗 API Gateway URL")
    url_input = st.text_input("API URL", API_GATEWAY_URL)
    st.markdown("---")
    st.caption("Developed using Sentence-Transformers + FAISS + Microservices")

API_GATEWAY_URL = url_input

# ===========================================
# SEARCH BAR
# ===========================================
query = st.text_input(
    "🔎 Enter your search query",
    placeholder="e.g. What is quantum physics?"
)

submit_btn = st.button("Search", use_container_width=True)

# ===========================================
# SEARCH HANDLER
# ===========================================
if submit_btn and query.strip():
    with st.spinner("Embedding query and searching..."):
        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/search",
                json={"query": query, "top_k": top_k}
            )
            data = response.json()
        except Exception as e:
            st.error(f"❌ API call failed: {e}")
            st.stop()

    if "results" not in data:
        st.error("No results returned from API.")
        st.stop()

    st.markdown("## 🔥 Search Results")
    st.markdown("---")

    # ===========================================
    # DISPLAY RESULTS
    # ===========================================
    for item in data["results"]:
        filename = item["filename"]
        score = item["score"]
        explanation = item["explanation"]
        preview = item["preview"]

        # ---------- Extract explanation ----------
        keywords = explanation.get("keyword_overlap", [])
        overlap_ratio = explanation.get("overlap_ratio", 0)
        sentences = explanation.get("top_sentences", [])

        # ===========================================
        # RESULT CARD
        # ===========================================
        st.markdown(f"""
        <div class="result-card">
            <h4>{filename}</h4>
            <div class="score-badge">Similarity Score: {score:.4f}</div>
            <p style='margin-top: 10px; color: #cccccc;'>{preview[:200]}...</p>
        </div>
        """, unsafe_allow_html=True)

        # ---------- Keyword Highlights ----------
        if keywords:
            st.write("**🔑 Keyword Overlap:** ")
            for kw in keywords:
                st.markdown(f"<span class='keyword'>{kw}</span>", unsafe_allow_html=True)

        st.write(f"**Overlap Ratio:** `{overlap_ratio:.3f}`")

        # ---------- Top Matched Sentences ----------
        if sentences:
            st.write("**💬 Top Matching Sentences:**")
            for s in sentences:
                st.info(f"{s['sentence']} (score: {s['score']:.4f})")

        # ---------- Expandable full document ----------
        with st.expander("📄 Full Document"):
            st.write(preview)

        st.markdown("---")
