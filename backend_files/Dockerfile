# Dockerfile - SuperKart Flask backend

FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and serialized model into the container
COPY app.py .
COPY superkart_model.joblib .

# Flask app listens on port 7860 (matches Codespaces forwarded port)
EXPOSE 7860

# Run the Flask app using gunicorn for a production-ready server
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:superkart_api"]
