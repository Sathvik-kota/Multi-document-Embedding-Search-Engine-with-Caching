import streamlit as st
import requests
import json
import html

API_GATEWAY_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Gemini Search",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded", # Changed from "collapsed" to "expanded"
)

# =======================
# GEMINI UI STYLING
# =======================
st.markdown("""
<style>
    /* Global Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff; /* White Background */
        color: #1f1f1f; /* Dark text for contrast */
    }

    /* --- INPUT FIELD FIX --- */
    /* 1. Remove the default Streamlit border/background on the container */
    .stTextInput > div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 24px !important; 
        box-shadow: none !important; 
    }
    
    /* 2. Style the actual input element */
    .stTextInput input {
        border-radius: 24px !important;
        background-color: #f0f4f9 !important; /* Light ash input */
        border: 1px solid transparent !important;
        color: #1f1f1f !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        transition: all 0.2s ease;
    }
    
    /* 3. Focus state - clean blue border, no default red overlay */
    .stTextInput input:focus {
        background-color: #ffffff !important;
        border-color: #0b57d0 !important; /* Gemini Blue */
        box-shadow: 0 0 0 2px rgba(11, 87, 208, 0.2) !important;
        outline: none !important;
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 20px;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    /* Primary Search Button */
    button[kind="primary"] {
        background: linear-gradient(90deg, #4b90ff, #ff5546);
        color: white;
    }
    button[kind="primary"]:hover {
        opacity: 0.9;
        box-shadow: 0 4px 12px rgba(75, 144, 255, 0.3);
    }

    /* Result Card - Light Ash Background */
    .result-card {
        background-color: #f0f4f9; /* Light Ash */
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: none; /* Removed border for cleaner look on light mode */
        transition: transform 0.2s;
    }
    .result-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* Typography in Cards */
    .card-title {
        color: #1f1f1f; /* Dark Title */
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .card-preview {
        color: #444746; /* Darker gray for readable preview */
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    /* Pills & Badges */
    .score-badge {
        background-color: #c4eed0; /* Light Green bg */
        color: #0f5223; /* Dark Green text */
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .keyword-pill {
        background-color: #c2e7ff; /* Light Blue bg */
        color: #004a77; /* Dark Blue text */
        padding: 2px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        margin-right: 6px;
        display: inline-block;
        margin-bottom: 4px;
    }

    /* Gradient Text for Header */
    .gradient-text {
        background: linear-gradient(to right, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
    }
    
    /* Custom Info Box */
    .stAlert {
        background-color: #f0f4f9;
        color: #1f1f1f;
    }
</style>
""", unsafe_allow_html=True)

# =======================
# SIDEBAR (Settings)
# =======================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    top_k = st.slider("Top-K Results", 1, 10, 5)
    url_input = st.text_input("API Endpoint", API_GATEWAY_URL)
    st.divider()
    st.subheader(" Evaluation")
    run_eval = st.button("Run Evaluation")
    st.divider()
    st.caption(" Powered by Sentence-Transformers")

API_GATEWAY_URL = url_input

# =======================
# MAIN HEADER (Gemini Style)
# =======================
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    # Use HTML for the gradient text title
    st.markdown('<div style="text-align: center; margin-bottom: 10px;"><span class="gradient-text">Hello, Explorer</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #444746; font-size: 1.2rem; margin-bottom: 30px;">How can I help you find documents today?</div>', unsafe_allow_html=True)


# =======================
# SEARCH BAR CENTERED
# =======================
# Centering the search bar using columns
sc1, sc2, sc3 = st.columns([1, 4, 1])

with sc2:
    query = st.text_input(
        "Search Query", # Label hidden by CSS/Config if needed, or set visibility hidden
        placeholder="Ask a question about your documents...",
        label_visibility="collapsed"
    )
    
    # Buttons row
    b1, b2, b3 = st.columns([2, 1, 2])
    with b2:
        submit_btn = st.button("Sparkle Search", type="primary", use_container_width=True)

# =======================
# SEARCH HANDLER
# =======================
if submit_btn and query.strip():

    # Gemini-style spinner
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

    # Results Header
    st.markdown("### ✨ Search Results")
    st.markdown("---")

    # =======================
    # DISPLAY RESULTS (Card Style)
    # =======================
    for item in data["results"]:
        filename = item["filename"]
        score = item["score"]
        explanation = item["explanation"]
        preview = item["preview"]
        full_text = item["full_text"]

        safe_preview = html.escape(preview)
        
        # Prepare keyword HTML
        keywords = explanation.get("keyword_overlap", [])
        keyword_html = ""
        if keywords:
            keyword_html = "".join([f"<span class='keyword-pill'>{kw}</span>" for kw in keywords])
        
        # Doc Icon (SVG) - Changed stroke to dark blue for visibility on light bg
        doc_icon = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0b57d0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>"""

        # Main Card Render
        st.markdown(f"""
        <div class="result-card">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div class="card-title">
                    {doc_icon} {filename}
                </div>
                <div class="score-badge">match: {score:.4f}</div>
            </div>
            <p class="card-preview">{safe_preview}...</p>
            <div style="margin-top: 10px;">
                {keyword_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Details Expander (Standard Streamlit but styled via global CSS)
        with st.expander(f"View Details & Full Text for {filename}"):
            
            overlap_ratio = explanation.get("overlap_ratio", 0)
            sentences = explanation.get("top_sentences", [])
            
            st.caption(f"Semantic Overlap Ratio: {overlap_ratio:.3f}")

            if sentences:
                st.markdown("**Key Excerpts:**")
                for s in sentences:
                    # Updated quote box for light mode
                    st.markdown(f"""
                    <div style="background: #ffffff; border-left: 3px solid #4285f4; padding: 10px; margin-bottom: 5px; border-radius: 0 8px 8px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <span style="color: #1f1f1f;">"{s['sentence']}"</span> 
                        <span style="color: #5e5e5e; font-size: 0.8em; margin-left: 10px;">(conf: {s['score']:.2f})</span>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("**📄 Full Document Content:**")
            st.code(full_text, language="text") # Using code block for better readability of raw text
if run_eval:
    st.info("Running evaluation... this may take 10–20 seconds.")

    from src.eval.evaluate import run_evaluation
    
    accuracy, results = run_evaluation()

    st.success(f"Evaluation Complete! Accuracy: {accuracy*100:.2f}%")

    st.write("### Incorrect Results")
    for r in results:
        if not r["correct"]:
            st.write(f"❌ Query: **{r['query']}**")
            st.write(f"Expected: `{r['expected']}`")
            st.write(f"Returned: `{r['returned']}`")
            st.markdown("---")
