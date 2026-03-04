FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure instance directory exists for the database
RUN mkdir -p instance

# Expose the application port
EXPOSE 5005

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5005", "--workers", "2", "app:app"]
