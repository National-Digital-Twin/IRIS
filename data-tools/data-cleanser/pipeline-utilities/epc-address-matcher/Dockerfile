FROM python:3.11.14-slim

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY match_uprn_os_places.py ./match_uprn_os_places.py

RUN chown -R appuser:appuser /app
USER appuser

CMD ["python", "match_uprn_os_places.py"]
