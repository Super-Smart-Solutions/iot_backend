FROM python:3.11.4-slim-bullseye as prod
RUN apt-get update && apt-get install -y \
  gcc \
  git \
  && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.4.2

# Configuring Poetry
RUN poetry config virtualenvs.create false

# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Initialize submodule and install dependencies
RUN git submodule update --init --recursive
RUN poetry install --only main

# Removing gcc after dependencies are installed
RUN apt-get purge -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . /app/src/
RUN poetry install --only main

# Command to run the application
CMD ["/usr/local/bin/python", "-m", "iot_backend"]

# Development stage
FROM prod as dev

RUN poetry install
