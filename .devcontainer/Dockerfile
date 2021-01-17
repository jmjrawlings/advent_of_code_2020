ARG MINIZINC_VERSION=2.5.3
ARG PYTHON_VERSION=3.9
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
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install poetry==$POETRY_VERSION

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install

# Ensure folders are created to volume mount VSCode extensions
RUN mkdir -p \
    ~/.vscode-server/extensions \
    ~/.vscode-server-insiders/extensions

# Install Docker CE CLI
RUN apt-get update \
    && apt-get install -y apt-transport-https ca-certificates curl gnupg2 lsb-release \
    && curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
    && echo "deb [arch=amd64] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli

# Install Docker Compose
RUN LATEST_COMPOSE_VERSION=$(curl -sSL "https://api.github.com/repos/docker/compose/releases/latest" | grep -o -P '(?<="tag_name": ").+(?=")') \
    && curl -sSL "https://github.com/docker/compose/releases/download/${LATEST_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose        

EXPOSE 10101