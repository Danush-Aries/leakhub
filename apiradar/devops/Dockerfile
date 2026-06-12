FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY ../../requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY ../backend ./backend

# Expose port
EXPOSE 8000

# Default: run the FastAPI server
CMD ["uvicorn", "backend.app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
