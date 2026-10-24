# Build dari root repo: docker build -f infra/docker/api.Dockerfile .
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /srv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
COPY packages packages
COPY apps/api apps/api
RUN uv sync --frozen --no-dev --package timesheet-api
EXPOSE 8000
CMD [".venv/bin/uvicorn", "app.main:app", "--app-dir", "apps/api", "--host", "0.0.0.0", "--port", "8000"]
