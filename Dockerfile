FROM python:3.6-slim

COPY requirements.txt app/

RUN pip install gunicorn pytest

RUN apt-get update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gcc build-essential \
	&& pip install -r /app/requirements.txt \
	&& DEBIAN_FRONTEND=noninteractive apt-get remove -y gcc build-essential \
	&& rm -rf /var/lib/apt/lists

ARG timezone

RUN ln -snf /usr/share/zoneinfo/$timezone /etc/localtime && echo $timezone > /etc/timezone

WORKDIR /app/src

ENV PYTHONUNBUFFERED 1

CMD ["gunicorn", "iwant_bot.start:app", "--reload", "--bind", "0.0.0.0:80", "--access-logfile", "-", "--worker-class", "aiohttp.GunicornWebWorker"]

COPY . /app/
