# Safe Python Executor

This API lets clients send a Python script that defines main(). The script is executed inside a locked down nsjail environment with:
	•	Limited CPU and memory
	•	A restricted filesystem
	•	No network access

After execution, the service returns:
	•	result: the JSON serializable return value of main()
	•	stdout: anything printed by the script

## Requirements

- Docker
- Poetry (for local development)

## Running with Docker

Run the container:
```bash
docker-compose up --build
```

The app will be available at `http://localhost:8080`

## Endpoints

- `GET /` - Returns a hello message
- `GET /health` - Health check endpoint
- `POST /execute`

