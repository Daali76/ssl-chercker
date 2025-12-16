# # Use Python 3.11 slim image as base
# FROM python:3.11-slim

# # Set working directory
# WORKDIR /app

# # Set environment variables
# ENV PYTHONUNBUFFERED=1
# ENV PYTHONDONTWRITEBYTECODE=1
# # Add current path to PYTHONPATH so Python can find the app module
# ENV PYTHONPATH=/app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     whois \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements file first
# COPY requirements.txt .

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# # Note: Copy entire directory. Since structure is modular, files are placed correctly.
# COPY . .

# # Create non-root user for security
# RUN useradd --create-home --shell /bin/bash ssl-checker && \
#     chown -R ssl-checker:ssl-checker /app

# USER ssl-checker

# EXPOSE 8000

# # Health check
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/ || exit 1

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev

COPY requirements.txt .


RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app


RUN apt-get update && apt-get install -y --no-install-recommends \
    whois \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY . .

RUN useradd --create-home --shell /bin/bash ssl-checker && \
    chown -R ssl-checker:ssl-checker /app

USER ssl-checker

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]