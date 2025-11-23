#!/bin/bash
echo " Starting multi-service document search system..."

# Start EMBEDDING service (port 9002)
python3 src/embedding_service/app.py --port 9002 &

# Start SEARCH service (port 9003)
python3 src/search_service/app.py --port 9003 &

# Start EXPLAIN service (port 9004)
python3 src/explain_service/app.py --port 9004 &

# Start API GATEWAY (port 8000)
python3 src/api_gateway/app.py --port 8000 &

sleep 5
echo "All microservices started!"

# Start Streamlit app (port 7860 for HF Spaces)
streamlit run src/ui/streamlit_app.py --server.port 7860 --server.address 0.0.0.0
