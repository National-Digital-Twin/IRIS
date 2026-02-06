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

RUN groupadd --system appuser && useradd --system --gid appuser --create-home appuser

ENV PATH /home/worker/.local/bin:${PATH}

COPY requirements.txt .
RUN --mount=type=secret,id=pat_token \
    export GITHUB_ACCESS_TOKEN=$(cat /run/secrets/pat_token) && \
    pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=appuser:appuser api api
COPY --chown=appuser:appuser developer-resources developer-resources
COPY --chown=appuser:appuser developer-resources/load_gpkg_to_postgis.py ./load_gpkg_to_postgis.py
COPY --chown=appuser:appuser alembic.ini entrypoint.sh setup.cfg version.txt ./

RUN chmod +x ./entrypoint.sh
USER appuser
ENTRYPOINT ["./entrypoint.sh"]
