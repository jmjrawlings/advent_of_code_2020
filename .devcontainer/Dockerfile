ARG MINIZINC_VERSION=2.5.3
ARG PYTHON_VERSION=3.8
ARG WAVE_VERSION=0.10.0
ARG POETRY_VERSION=1.1.4

FROM minizinc/minizinc:$MINIZINC_VERSION as builder

FROM mcr.microsoft.com/vscode/devcontainers/python:$PYTHON_VERSION

COPY --from=builder /usr/local/share/minizinc /usr/local/share/minizinc
COPY --from=builder /usr/local/bin/ /usr/local/bin/

ARG WAVE_VERSION
ARG POETRY_VERSION

# Install Wave
RUN wget -c https://github.com/h2oai/wave/releases/download/v$WAVE_VERSION/wave-$WAVE_VERSION-linux-amd64.tar.gz -O - | tar -xz && \
    mv ./wave-$WAVE_VERSION-linux-amd64 /wave

# Install Poetry
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install poetry==$POETRY_VERSION

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install

EXPOSE 10101