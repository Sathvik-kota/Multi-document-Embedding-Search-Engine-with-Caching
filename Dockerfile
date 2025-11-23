# -------------------------
# Base image
# -------------------------
ENV PYTHONPATH="/home/user/app"
FROM python:3.11-slim

# Allow root user (HF Spaces supports this for Docker)
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PORT=7860

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl git build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy whole project
COPY . .

# Make startup executable
RUN chmod +x /app/start.sh

EXPOSE 7860

CMD ["bash", "/app/start.sh"]
