FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies first for better layer caching.
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy backend source code.
COPY app ./app

EXPOSE 8000

# Start FastAPI server.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
