# 1. Imagem base moderna e leve
FROM python:3.10-slim

# 2. Instala Java + dependências essenciais
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-11-jre-headless \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Diretório de trabalho
WORKDIR /app

# 4. Copia apenas requirements primeiro (cache)
COPY requirements.txt .

# 5. Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Baixa o JAR do tabula (evita download em runtime)
RUN wget -q https://github.com/tabulapdf/tabula-java/releases/download/v1.0.5/tabula-1.0.5-jar-with-dependencies.jar \
    -O /usr/local/lib/tabula.jar

# 7. Variável para tabula-py encontrar o JAR
ENV TABULA_JAR=/usr/local/lib/tabula.jar

# 8. Copia apenas o código necessário
COPY main.py .
# Se tiver pastas: COPY app/ ./app/

# 9. Porta do Railway
EXPOSE 8080

# 10. Variáveis de ambiente
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=8080

# 11. Usa Gunicorn com worker otimizado
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 "main:app"
