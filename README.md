# Safe Python Executor

This API lets clients send a Python script that defines main(). The script is executed inside a locked down nsjail environment with:
- Limited CPU and memory
- A restricted filesystem
- No network access

After execution, the service returns:
- result: the JSON serializable return value of main()
- stdout: anything printed by the script

## Requirements

- Docker
- Poetry (for local development)

## Running Locally

Run the container:
```bash
docker-compose up --build
```

The app will be available at `http://localhost:8080`

### Running without nsjail

Some environments (e.g. Cloud Run on gVisor) block the kernel features nsjail needs. To exercise the non-nsjail execution path, set:

```bash
export ENABLE_NSJAIL=false
```

For Docker Compose, add `ENABLE_NSJAIL=false` under `services.api.environment` and run `docker-compose up --build`. The wrapper still validates scripts, but isolation relies on the container runtime instead of nsjail.

### Test with curl

Local (docker-compose port 8080):
```bash
curl -X POST http://localhost:8080/execute \
  -H 'Content-Type: application/json' \
  -d '{"script": "def main():\n    return 42"}'
```

Production:
```bash
curl -X POST https://safe-python-executor-538469180276.us-central1.run.app/execute \
  -H 'Content-Type: application/json' \
  -d '{"script": "def main():\n    return 42"}'
```

## Production

The production API is available at:
```
https://safe-python-executor-538469180276.us-central1.run.app/execute
```

## Endpoints

- `GET /` - Returns a hello message
- `GET /health` - Health check endpoint
- `POST /execute` - Execute a Python script
