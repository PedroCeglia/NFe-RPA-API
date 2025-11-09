# 1. Base estável com OpenJDK 11 disponível
FROM python:3.10-slim-bullseye

# 2. Instala Java + dependências
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-11-jre-headless \
        gcc \
        python3-dev \
        ca-certificates \
        wget \
    && rm -rf /var/lib/apt/lists/*

# 3. Diretório de trabalho
WORKDIR /app

# 4. Copia requirements primeiro (melhor cache)
COPY requirements.txt .

# 5. Instala pacotes Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Baixa o JAR do tabula (evita falha em runtime)
RUN wget -q https://github.com/tabulapdf/tabula-java/releases/download/v1.0.5/tabula-1.0.5-jar-with-dependencies.jar \
    -O /usr/local/lib/tabula.jar

# 7. Configura tabula-py
ENV TABULA_JAR=/usr/local/lib/tabula.jar

# 8. Copia apenas o necessário
COPY main.py .

# 9. Porta do Railway
EXPOSE 8080

# 10. Variáveis
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=8080

# 11. Inicia com Gunicorn
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 "main:app"
