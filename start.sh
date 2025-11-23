#!/bin/bash
echo "🚀 Starting multi-service system..."

export PYTHONPATH="/app"

# DOC SERVICE
uvicorn src.doc_service.app:app --host 0.0.0.0 --port 9001 &
# EMBED SERVICE
uvicorn src.embed_service.app:app --host 0.0.0.0 --port 9002 &
# SEARCH SERVICE
uvicorn src.search_service.app:app --host 0.0.0.0 --port 9003 &
# EXPLAIN SERVICE
uvicorn src.explain_service.app:app --host 0.0.0.0 --port 9004 &
# API GATEWAY
uvicorn src.api_gateway.app:app --host 0.0.0.0 --port 8000 &

sleep 5
echo "✅ All microservices running!"

streamlit run src/ui/streamlit_app.py \
  --server.port 7860 \
  --server.address 0.0.0.0
