FROM python:3.6-alpine

COPY requirements.txt /app/

RUN true \
	&& pip install gunicorn \
	&& pip install -r /app/requirements.txt \
	&& true

WORKDIR /app/src

CMD ["gunicorn", "iwant_bot.start:app", "--reload", "--bind", "0.0.0.0:8080", "--worker-class", "aiohttp.GunicornWebWorker"]
