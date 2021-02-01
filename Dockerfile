ARG MINIZINC_VERSION=2.5.3
ARG PYTHON_VERSION=3.9
ARG WAVE_VERSION=0.11.0
ARG POETRY_VERSION=1.1.4
ARG ZSH_THEME=dst

FROM minizinc/minizinc:$MINIZINC_VERSION as minizinc-base

FROM python:$PYTHON_VERSION-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    WAVE_PATH="/wave"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

COPY --from=minizinc-base /usr/local/share/minizinc /usr/local/share/minizinc
COPY --from=minizinc-base /usr/local/bin/minizinc /usr/local/bin/minizinc
COPY --from=minizinc-base /usr/local/bin/fzn-* /usr/local/bin

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    wget

# Install Wave
ARG WAVE_VERSION
RUN wget -c https://github.com/h2oai/wave/releases/download/v$WAVE_VERSION/wave-$WAVE_VERSION-linux-amd64.tar.gz -O - | tar -xz && \
    mv ./wave-$WAVE_VERSION-linux-amd64 $WAVE_PATH

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
ARG POETRY_VERSION
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# dependency-base is used to build common dependencies
FROM python-base as dependency-base

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-dev --no-root

# 'development' stage installs all dev deps and can be used to develop code.
# For example using docker-compose to mount local volume under /app
FROM python-base as dev

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    apt-utils \
    git \
    openssh-client \
    fonts-powerline \
    make \
    gnupg2 \
    iproute2 \
    procps \
    lsof \
    htop \
    net-tools \
    psmisc \
    rsync \
    ca-certificates \
    unzip \
    zip \
    nano \
    vim-tiny \
    less \
    jq \
    lsb-release \
    apt-transport-https \
    dialog \
    libc6 \
    libgcc1 \
    libkrb5-3 \
    libgssapi-krb5-2 \
    libicu[0-9][0-9] \
    liblttng-ust0 \
    libstdc++6 \
    zlib1g \
    locales \
    sudo \
    ncdu \
    man-db \
    strace \
    libssl1.1

# Install Docker CE CLI
RUN curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
    && echo "deb [arch=amd64] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli

# Install Docker Compose
RUN LATEST_COMPOSE_VERSION=$(curl -sSL "https://api.github.com/repos/docker/compose/releases/latest" | grep -o -P '(?<="tag_name": ").+(?=")') \
    && curl -sSL "https://github.com/docker/compose/releases/download/${LATEST_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose        

# Copying poetry and its virtual env 
COPY --from=dependency-base $POETRY_HOME $POETRY_HOME
COPY --from=dependency-base $PYSETUP_PATH $PYSETUP_PATH

# Run Poetry full install - this will use the runtime deps from the dependency-base layer
WORKDIR $PYSETUP_PATH
RUN poetry install --no-root

# We now disable venv creation as the venv is already on PATH
ENV POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_CREATE=false

# Install and set ZSH as the shell
ARG ZSH_THEME
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.1/zsh-in-docker.sh)" -- \
    -t $ZSH_THEME \
    -p git \
    -p docker

# 'production' stage uses the clean 'python-base' stage and copyies
# in only our runtime deps that were installed in the 'dependency-base'
FROM python-base as prod