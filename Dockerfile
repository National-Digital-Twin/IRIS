FROM python:3.12-slim
ARG PIP_EXTRA_INDEX_URL
ARG APP_USER=appuser
ARG APP_UID=10001

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

RUN groupadd --gid ${APP_UID} ${APP_USER} \
    && useradd --uid ${APP_UID} --gid ${APP_UID} --create-home --shell /usr/sbin/nologin ${APP_USER}

WORKDIR /app

ENV PATH /home/worker/.local/bin:${PATH}

COPY requirements.txt .
RUN --mount=type=secret,id=pat_token \
    export GITHUB_ACCESS_TOKEN=$(cat /run/secrets/pat_token) && \
    pip install --no-cache-dir --upgrade -r requirements.txt
COPY developer-resources/load_gpkg_to_postgis.py load_gpkg_to_postgis.py
COPY README.md ./README.md
COPY alembic.ini ./alembic.ini
COPY entrypoint.sh ./entrypoint.sh
COPY api ./api
COPY developer-resources/load_gpkg_to_postgis.py developer-resources/load_gpkg_to_postgis.py
COPY developer-resources/sync_region_fks_dbu.py developer-resources/sync_region_fks_dbu.py

RUN chmod +x ./entrypoint.sh
RUN chown -R ${APP_USER}:${APP_USER} /app
USER ${APP_USER}
ENTRYPOINT ["./entrypoint.sh"]
