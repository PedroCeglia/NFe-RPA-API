FROM python:3.10-slim-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-11-jre-headless \
        gcc \
        python3-dev \
        ca-certificates \
        wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baixa tabula JAR
RUN wget -q https://github.com/tabulapdf/tabula-java/releases/download/v1.0.5/tabula-1.0.5-jar-with-dependencies.jar \
    -O /usr/local/lib/tabula.jar
ENV TABULA_JAR=/usr/local/lib/tabula.jar

# COPIA TODAS AS PASTAS E ARQUIVOS
COPY . .

# Porta do Railway
EXPOSE 8080
ENV PORT=8080

# Inicia
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 "main:app"
