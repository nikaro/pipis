FROM python:3.6

WORKDIR  /app/

RUN pip install --no-cache-dir poetry

COPY pyproject.* /app/

RUN poetry install

COPY . /app/

CMD ["poetry", "run", "python", "-m", "pytest"]
