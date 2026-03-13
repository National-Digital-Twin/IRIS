FROM debian:stable-slim
RUN useradd --create-home --shell /bin/bash appuser \
    && apt-get update \
    && apt-get install -y postgresql-client awscli \
    && rm -rf /var/lib/apt/lists/*

COPY postgres-to-s3-transfer.sh /postgres-to-s3-transfer.sh
RUN chown appuser:appuser /postgres-to-s3-transfer.sh
USER appuser

ENTRYPOINT ["/bin/bash", "/postgres-to-s3-transfer.sh"]
