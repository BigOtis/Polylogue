FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Optional but recommended
EXPOSE 8080

# Use gunicorn for production readiness
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "server:app"]
