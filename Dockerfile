FROM python:3.12-alpine

ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . .

RUN uv sync --all-extras --all-groups

ENV PATH="/app/.venv/bin:$PATH"

RUN pytest

RUN uv build --wheel

EXPOSE 8000
CMD ["uvicorn", "egg_timer.app:app", "--host", "0.0.0.0", "--port", "8000"]
