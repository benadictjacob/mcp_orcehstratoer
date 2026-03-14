# Use Python 3.11 as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose MCP port (if applicable for transport)
# MCP usually runs over stdio, but some frameworks use HTTP/SSE
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["python", "validation_agent.py"]
