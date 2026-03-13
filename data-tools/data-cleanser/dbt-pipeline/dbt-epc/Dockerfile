FROM python:3.11.14-slim

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DBT_PROFILES_DIR=/app
ENV PYTHONPATH=/app:/app/utils

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dbt-epc/packages.yml ./packages.yml
COPY dbt-epc/dbt_project.yml ./dbt_project.yml
COPY dbt-epc/profiles.yml ./profiles.yml
COPY dbt-epc/models ./models
COPY utils ./utils

RUN chown -R appuser:appuser /app
USER appuser

RUN dbt deps --project-dir .

CMD ["dbt", "run", "--project-dir", "."]
