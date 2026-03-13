# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app


COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv

RUN uv sync

# Copy the Python script into the container's working directory
COPY *.py .

# Specify the command to run when the container starts
CMD ["python", "run_pipeline.py"]