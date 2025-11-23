#!/bin/bash

echo "🚀 Starting multi-service document search system..."

# ---------------------------------------------
# Ensure Python can resolve src/ as a package
# ---------------------------------------------
export PYTHONPATH="/app"

# ---------------------------------------------
# Start all microservices as MODULES (required!)
# ---------------------------------------------
python3 -m src.doc_service.app --port 9001 &
python3 -m src.embed_service.app --port 9002 &
python3 -m src.search_service.app --port 9003 &
python3 -m src.explain_service.app --port 9004 &
python3 -m src.api_gateway.app --port 8000 &

sleep 5
echo "✅ All microservices started!"

# ---------------------------------------------
# Start Streamlit (HF Spaces runs on port 7860)
# ---------------------------------------------
streamlit run src/ui/streamlit_app.py \
    --server.port 7860 \
    --server.address 0.0.0.0
