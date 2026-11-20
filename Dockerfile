FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BSR_ENV=production \
    BSR_HOST=0.0.0.0 \
    BSR_PORT=8000 \
    BSR_DATABASE=/data/bsr.db \
    BSR_SEED_ON_START=0

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY migrations ./migrations
COPY wsgi.py run_prod.py ./

# SQLite keeps its database, WAL and SHM files in one directory: mount a
# volume here, otherwise every container restart starts from an empty schema.
RUN mkdir -p /data && chown -R nobody:nogroup /data
VOLUME ["/data"]

USER nobody
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4).status == 200 else 1)"

CMD ["python", "run_prod.py"]
