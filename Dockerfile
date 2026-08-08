FROM python:3.11-slim

# نصب Xray
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget unzip ca-certificates && \
    wget -q https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip && \
    unzip Xray-linux-64.zip -d /usr/local/bin/ && \
    rm Xray-linux-64.zip && \
    chmod +x /usr/local/bin/xray && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000 8080

CMD ["/bin/bash", "/app/start.sh"]
