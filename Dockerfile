FROM python:3.12-slim
ARG PIP_EXTRA_INDEX_URL

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cargo \
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

COPY . .

CMD ["python", "api/main.py", "--host", "0.0.0.0"]
