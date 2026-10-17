# Etapa 1: builder
FROM python:3.11-slim AS builder

WORKDIR /usr/local/share/api

# Instala dependencias necesarias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -t /deps

# Copia el resto del código
COPY app.py .
COPY manage_agenda.py .
COPY .env.example .
COPY src/ src/
COPY sql/ sql/

# Etapa 2: imagen final distroless
FROM gcr.io/distroless/python3-debian12

WORKDIR /usr/local/share/api

# Copia dependencias y código desde la etapa builder
COPY --from=builder /deps /usr/lib/python3.11/site-packages
COPY --from=builder /usr/local/share/api /usr/local/share/api

ENV PYTHONPATH=/usr/lib/python3.11/site-packages

EXPOSE 5000

# Comando de ejecución (Gunicorn)
CMD ["-m", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
