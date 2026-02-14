FROM docker.io/python:3.12-slim

WORKDIR /app

# Disable creation of .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install ALL Playwright dependencies in one package + additional ones
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Installing Playwright with system dependencies
RUN pip install --no-cache-dir playwright && \
    playwright install --with-deps chromium

# Copy requirements
COPY requirements.txt .
# Installing Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only src
COPY src/ .

# Launching the service
CMD ["python", "single_page_downloader_svc.py"]