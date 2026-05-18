FROM python:3.12-slim

WORKDIR /app

# 安装 ngrok
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
      | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" \
      | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && apt-get install -y ngrok && \
    apt-get purge -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY pyproject.toml .
COPY model_mapping.json .
COPY start.py .
COPY mimo2api/ mimo2api/

RUN mkdir -p /app/logs /app/users

EXPOSE 8000

CMD ["python", "main.py"]
