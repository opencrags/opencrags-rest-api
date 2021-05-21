# opencrags-rest-api

## Build

Images will be built and pushed by github actions.

### Local

```bash
docker-compose up -d
```

## Development

Everything is automatically installed inside the docker container. The local
source code is mounted and the server watches for changes.

```bash
docker-compose up dev
```
