FROM python:3.6-slim

COPY requirements.txt app/

RUN pip install gunicorn pytest && pip install -r /app/requirements.txt

ARG timezone

RUN ln -snf /usr/share/zoneinfo/$timezone /etc/localtime && echo $timezone > /etc/timezone

WORKDIR /app/src

ENV PYTHONUNBUFFERED 1

CMD ["gunicorn", "iwant_bot.start:app", "--reload", "--bind", "0.0.0.0:80", "--access-logfile", "-", "--worker-class", "aiohttp.GunicornWebWorker"]

COPY . /app/
