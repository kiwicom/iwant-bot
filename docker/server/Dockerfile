FROM python:3.6

RUN true \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		git \
	&& apt-get clean \
	&& true

RUN true \
	&& git clone https://github.com/kiwicom/iwant-bot.git \
	#&& pip install -r iwantbot/requirements.txt \
	&& true

CMD [ "python", "iwantbot/your-daemon-or-script.py" ]
