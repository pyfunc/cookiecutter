FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY . .

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

EXPOSE 50051

CMD ["python", "server.py"]
