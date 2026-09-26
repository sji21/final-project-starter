FROM python:3.12-slim
WORKDIR /app
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock
COPY app ./app
COPY web ./web
COPY packs ./packs
RUN useradd --uid 10001 --create-home appuser && mkdir /data && chown appuser:appuser /data
ENV APP_DATA_DIR=/data
USER appuser
EXPOSE 8765
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8765", "--workers", "1"]

