FROM python:3.11-slim

WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port that Tornado uses
EXPOSE 8888

# Run the application
CMD ["python", "Endpoint.py"] 