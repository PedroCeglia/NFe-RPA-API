# 1. Usar uma imagem base do Python
FROM python:3.10-buster

# 2. Instalar o Java (openjdk-11)
RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    rm -rf /var/lib/apt/lists/*

# 3. Definir o diretório de trabalho no container
WORKDIR /app

# 4. Copiar o arquivo de dependências para o container
COPY requirements.txt .

# 5. Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar o restante dos arquivos do projeto para o container
COPY . .

# 7. Expor a porta que a API vai usar
EXPOSE 5000

# 8. Definir a variável de ambiente para rodar o Flask
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# 9. Instalar o Gunicorn (se não estiver listado em requirements.txt)
RUN pip install gunicorn

# 10. Comando para rodar o servidor usando Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
