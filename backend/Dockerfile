FROM python:3.12-slim
ARG PIP_EXTRA_INDEX_URL

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cargo \
    gdal-bin \
    git \
    libffi-dev \
    librdkafka-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    python3-dev

WORKDIR /app

ENV PATH /home/worker/.local/bin:${PATH}

COPY requirements.txt .
RUN --mount=type=secret,id=pat_token \
    export GITHUB_ACCESS_TOKEN=$(cat /run/secrets/pat_token) && \
    pip install --no-cache-dir --upgrade -r requirements.txt

COPY developer-resources/load_gpkg_to_postgis.py developer-resources/load_gpkg_to_postgis.py
COPY developer-resources/sync_region_fks_dbu.py developer-resources/sync_region_fks_dbu.py
COPY api/ api/
COPY unit_tests/ unit_tests/
COPY alembic.ini .
COPY entrypoint.sh .
COPY publish.sh .
COPY pytest.ini .
COPY setup.cfg .
COPY version.txt .

RUN adduser --system --no-create-home appuser && chmod +x ./entrypoint.sh

USER appuser
ENTRYPOINT ["./entrypoint.sh"]
