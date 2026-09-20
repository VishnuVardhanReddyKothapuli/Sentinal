FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PORT=7860 DATA_DIR=/app/data ENABLE_AI_MODELS=true AUTO_CREATE_TABLES=false ENVIRONMENT=production
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr libglib2.0-0 libgl1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ARG INSTALL_AI=true
RUN if [ "$INSTALL_AI" = "true" ]; then pip install --no-cache-dir 'torch>=2.5,<3' 'torchvision>=0.20,<1' --index-url https://download.pytorch.org/whl/cpu && pip install --no-cache-dir -r requirements-ai.txt; fi
RUN useradd --uid 1000 --create-home sentinel && mkdir -p /app/data /home/sentinel/.cache && chown -R sentinel:sentinel /app /home/sentinel/.cache
USER sentinel
EXPOSE 7860
CMD ["sh", "-c", "export HF_HOME=${HF_HOME:-$DATA_DIR/models}; alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860} --workers 1"]
