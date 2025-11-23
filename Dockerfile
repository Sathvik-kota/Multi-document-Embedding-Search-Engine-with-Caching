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
    PORT=7860 \
    DATA_FOLDER="/app/docs"

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
# Debug: list /app/docs & warn about big files
# -------------------------
RUN echo ">>> /app/docs contents (if any) <<<" && \
    if [ -d "/app/docs" ]; then ls -la /app/docs || true; else echo "/app/docs not found"; fi && \
    echo ">>> Checking for files larger than 100MB <<<" && \
    if [ -d "/app" ]; then find /app -type f -size +100M -exec ls -lh {} \; || true; else echo "no /app dir"; fi

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
