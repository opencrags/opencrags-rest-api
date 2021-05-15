# opencrags-rest-api

## Build

### Locally

```bash
docker build . -t opencrags-rest-api
```

## Run

```bash
docker run -p 0.0.0.0:8000:8000 opencrags-rest-api
```

## Development

```bash
uvicorn app.main:app --reload
```
