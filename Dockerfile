FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

# Install all packages with pip directly
RUN pip install fastapi uvicorn python-multipart \
    spacy psycopg2-binary boto3 mlflow \
    transformers torch pdfplumber openai

# Download spaCy model with pip (not uv run)
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Copy app files
COPY *.py .
COPY rubric.json .
COPY schema.sql .

EXPOSE 8000

CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", "--port", "8000"]