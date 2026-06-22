FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (better layer caching).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application.
COPY backend ./backend
COPY frontend ./frontend
RUN mkdir -p data

# The key is provided at runtime via an environment variable,
# never baked into the image.
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
