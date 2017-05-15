FROM python:3.6-alpine

COPY requirements.txt app/

RUN pip install gunicorn \
	&& pip install -r /app/requirements.txt

ARG timezone

# This RUN operation is trivial in comparison with download of Python dependencies, so it has its own RUN section.
RUN apk add --update tzdata \
	&& ln -snf "/usr/share/zoneinfo/$timezone" /etc/localtime \
	&& echo $timezone > /etc/timezone \
	&& rm -rf /var/cache/apk/*

WORKDIR /app/src

CMD ["gunicorn", "iwant_bot.start:app", "--reload", "--bind", "0.0.0.0:80", "--worker-class", "aiohttp.GunicornWebWorker"]

COPY . /app/
