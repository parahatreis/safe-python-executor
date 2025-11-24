FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create virtual env and install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8080

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "app:app"]

