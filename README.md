# opencrags-rest-api

## Build

Images will be built and pushed by github actions.

### Local

```bash
docker build . -t opencrags-rest-api
```

```bash
docker run -p 0.0.0.0:8000:8000 opencrags-rest-api
```

## Development

### Install

#### Recommended
Install pyenv
```bash
curl https://pyenv.run | bash
```

Install python 3.8
```bash
pyenv install 3.8.8
```

#### Install with poetry
Install poetry
```bash
pyenv local 3.8.8
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Install python dependencies
```bash
poetry install
```

### Development server
```bash
uvicorn app.main:app --reload
```
