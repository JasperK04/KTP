FROM ghcr.io/benoitc/gunicorn:latest

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml ./

USER root

RUN echo "3.12" > .python-version

RUN uv sync

ENV PATH="/app/.venv/bin:$PATH"

COPY src/ ./src/
COPY main.py ./

CMD ["uv", "run", "-m", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "main:app"]
