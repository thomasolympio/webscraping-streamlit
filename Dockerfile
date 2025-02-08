# Utilizando imagem base com Python
FROM python:3.9

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando os arquivos do projeto
COPY . /app

# Instalando as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expondo a porta do Streamlit
EXPOSE 8501

# Comando para rodar o aplicativo Streamlit
CMD ["streamlit", "run", "app/dashboard.py", "--server.port=8501", "--server.enableCORS=false"]
