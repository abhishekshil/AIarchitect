# Multi-stage image for production-style runs; local dev typically uses `uvicorn --reload` on host.
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

FROM base AS builder
RUN pip install uv
COPY pyproject.toml README.md ./
COPY src ./src
RUN uv pip install --system .

FROM base AS runtime
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src ./src
EXPOSE 8000
CMD ["uvicorn", "solution_planning_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
