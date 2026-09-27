# Dockerfile - SuperKart Streamlit frontend

FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Streamlit's default port
EXPOSE 8501

# Run the Streamlit app, binding to all interfaces so it is reachable
# from outside the container (e.g. via the Codespaces forwarded port)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
