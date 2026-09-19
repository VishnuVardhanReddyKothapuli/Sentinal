FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr libglib2.0-0 libgl1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ARG INSTALL_AI=false
RUN if [ "$INSTALL_AI" = "true" ]; then pip install --no-cache-dir -r requirements-ai.txt; fi
RUN useradd --create-home sentinel && mkdir -p /app/data /home/sentinel/.cache && chown -R sentinel:sentinel /app /home/sentinel/.cache
USER sentinel
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
