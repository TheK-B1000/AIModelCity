# Serving image for AI Model Foundation
FROM python:3.11-slim

WORKDIR /app

# Install deps (adjust to your requirements.txt location)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy foundation and model code (or mount at runtime)
COPY foundation/ ./foundation/
COPY models/ ./models/
COPY pipelines/ ./pipelines/

# Default: run a simple HTTP server that loads model and serves predictions
# Override CMD in k8s with model name and artifact path
ENV MODEL_NAME=""
ENV ARTIFACT_PATH=""
EXPOSE 8080
CMD ["python", "-m", "http.server", "8080"]
