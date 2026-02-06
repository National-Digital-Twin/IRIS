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

COPY --chmod=0444 requirements.txt ./requirements.txt
RUN --mount=type=secret,id=pat_token \
    export GITHUB_ACCESS_TOKEN=$(cat /run/secrets/pat_token) && \
    pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chmod=0555 api api
COPY --chmod=0555 developer-resources developer-resources
COPY --chmod=0444 alembic.ini ./alembic.ini
COPY --chmod=0444 setup.cfg ./setup.cfg
COPY --chmod=0444 version.txt ./version.txt
COPY --chmod=0555 entrypoint.sh ./entrypoint.sh
USER appuser
ENTRYPOINT ["./entrypoint.sh"]
