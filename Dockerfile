# -------------------------
# Base image
# -------------------------
FROM python:3.11-slim

# -------------------------
# Working directory
# -------------------------
WORKDIR /app

# -------------------------
# Python buffer settings
# -------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PORT=7860

# -------------------------
# Install system dependencies
# -------------------------
RUN apt-get update && apt-get install -y \
    curl git build-essential && \
    rm -rf /var/lib/apt/lists/*

# -------------------------
# Install Python deps FIRST (cache)
# -------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------------
# Copy entire project
# -------------------------
COPY . .

# -------------------------
# Make start.sh executable
# -------------------------
RUN chmod +x /app/start.sh

# -------------------------
# Expose Streamlit port
# -------------------------
EXPOSE 7860

# -------------------------
# Start the full system
# -------------------------
CMD ["bash", "/app/start.sh"]
