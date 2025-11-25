FROM python:3.12-slim

WORKDIR /app

# Install nsjail
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential git flex bison \
        protobuf-compiler libprotobuf-dev pkg-config \
        libnl-route-3-dev libcap-dev && \
    git clone --depth 1 https://github.com/google/nsjail.git /tmp/nsjail && \
    cd /tmp/nsjail && make && \
    cp nsjail /usr/local/bin/ && chmod +x /usr/local/bin/nsjail && \
    cd / && rm -rf /tmp/nsjail && \
    apt-get install -y --no-install-recommends libnl-route-3-200 libcap2 libprotobuf32t64 && \
    apt-get purge -y build-essential git flex bison protobuf-compiler libprotobuf-dev pkg-config libnl-route-3-dev libcap-dev && \
    apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install poetry and dependencies
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi

# Copy application code
COPY app/ ./app/
RUN chmod +x /app/app/execution/wrapper.py

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "app:app"]

