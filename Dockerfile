FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    SANDBOX_ROOT=/tmp/nsjail_exec
WORKDIR /app

# Install nsjail and its runtime deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential git flex bison \
        protobuf-compiler libprotobuf-dev pkg-config \
        libnl-route-3-dev libcap-dev && \
    git clone --depth 1 https://github.com/google/nsjail.git /tmp/nsjail && \
    cd /tmp/nsjail && make && \
    cp nsjail /usr/local/bin/ && chmod +x /usr/local/bin/nsjail && \
    cd / && rm -rf /tmp/nsjail && \
    apt-get install -y --no-install-recommends \
        libnl-route-3-200 libcap2 libprotobuf32t64 && \
    apt-get purge -y \
        build-essential git flex bison \
        protobuf-compiler libprotobuf-dev pkg-config \
        libnl-route-3-dev libcap-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi

# Copy application code (includes nsjail_common.cfg)
COPY app/ ./app/

# Make sure wrapper is executable
RUN chmod +x /app/app/execution/wrapper.py

# Create non-root user and per run temp base
RUN useradd -m sandbox && \
    mkdir -p "${SANDBOX_ROOT}" && \
    chown -R sandbox:sandbox "${SANDBOX_ROOT}" /app

# Run the service as the sandbox user so nsjail stays in user-mode
USER sandbox

EXPOSE 8080

# Start Flask app via gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "app:app"]