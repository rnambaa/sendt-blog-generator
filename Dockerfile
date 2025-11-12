FROM python:3.12-slim

WORKDIR /app

# Copy dependencies first (for better caching)
COPY requirements.txt .

# Install dependencies (without cache to reduce image size)
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire project
COPY . .

# Expose the FastAPI port
EXPOSE 8080

# Set environment variable for production
ENV PYTHONUNBUFFERED=1

# Start FastAPI using uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
