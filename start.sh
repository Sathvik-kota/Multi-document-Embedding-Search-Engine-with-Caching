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

# Wait for all services to boot
sleep 8
echo "✅ All microservices running!"

# --------------------------
# AUTO INITIALIZE PIPELINE
# --------------------------
echo "🔁 Running auto-initialize (load → embed → build index)..."

MAX_TRIES=5
DELAY=4
i=1

while [ $i -le $MAX_TRIES ]; do
  echo "Attempt $i / $MAX_TRIES ..."
  STATUS=$(curl -s -o /tmp/init_output.json -w "%{http_code}" -X POST http://localhost:8000/initialize)

  if [ "$STATUS" = "200" ]; then
    echo "✅ Auto-initialize complete."
    cat /tmp/init_output.json
    break
  fi

  echo "⚠ Initialization failed (status $STATUS). Retrying in $DELAY seconds..."
  sleep $DELAY
  i=$((i+1))
done

if [ $i -gt $MAX_TRIES ]; then
  echo "❌ Auto-initialize failed after $MAX_TRIES attempts."
fi

# --------------------------
# Start Streamlit UI
# --------------------------
streamlit run src/ui/streamlit_app.py \
  --server.port=7860 \
  --server.address=0.0.0.0
