FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=6 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:80/healthz', timeout=3)"

CMD ["python", "-m", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:80", "--workers", "1", "--access-logfile", "-", "--error-logfile", "-", "--capture-output"]
