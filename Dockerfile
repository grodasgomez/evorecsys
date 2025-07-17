FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Create a virtual environment
RUN python -m venv /venv

# Activate the virtual environment
ENV PATH="/venv/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
