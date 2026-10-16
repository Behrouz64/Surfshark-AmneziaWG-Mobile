# Lightweight container for Surfshark AmneziaWG Mobile Scanner
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system build dependencies for Pillow
RUN apk add --no-cache \
    gcc \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    libjpeg-turbo-dev

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY core/ ./core/
COPY data/ ./data/
COPY static/ ./static/
COPY templates/ ./templates/
COPY server.py cli.py ./

# Expose web server port
EXPOSE 8080

# Run mobile web server
ENTRYPOINT ["python", "server.py", "--host", "0.0.0.0", "--port", "8080"]
