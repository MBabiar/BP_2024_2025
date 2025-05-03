FROM python:3.12.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RUNNING_IN_DOCKER=true 

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/

RUN mkdir -p /app/dashboard_app/src /app/config

# Copy files and configure Poetry to install dependencies into global python environment
COPY pyproject.toml /app/
COPY src/ /app/dashboard_app/src/
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

EXPOSE 8080

WORKDIR /app

CMD ["python", "dashboard_app/src/app.py"]