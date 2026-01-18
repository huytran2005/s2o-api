# 1. Base image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# 4. Install python dependencies
COPY requirements.docker.txt .
RUN pip install --no-cache-dir -r requirements.docker.txt

# 5. Copy source code
COPY . .

# 6. Copy and setup entrypoint
RUN chmod +x entrypoint.sh

# 7. Expose port
EXPOSE 8000

# 8. Entrypoint (start + migrate)
ENTRYPOINT ["./entrypoint.sh"]
