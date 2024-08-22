FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.3.1 /uv /bin/uv

ADD . /app
WORKDIR /app

RUN uv sync

CMD ["uv", "run", "main.py"]