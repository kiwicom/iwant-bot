FROM python:3.6-alpine

COPY requirements.txt /app/

RUN pip install gunicorn \
	&& pip install -r /app/requirements.txt

WORKDIR /app/src

CMD ["gunicorn", "iwant_bot.start:app", "--reload", "--bind", "0.0.0.0:80", "--worker-class", "aiohttp.GunicornWebWorker"]
