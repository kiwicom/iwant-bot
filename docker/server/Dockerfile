FROM python:3.6

RUN true \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		git vim-tiny \
	&& apt-get clean \
	&& true

RUN true \
	&& git clone https://github.com/kiwicom/iwant-bot.git /iwant-bot-cloned \
	&& ln -s /iwant-bot-cloned /iwant-bot \
	&& (cd iwant-bot && git checkout docker-support) \
	&& pip install -r iwant-bot/requirements.txt \
	&& true

CMD [ "python", "/iwant-bot/src/iwant_bot/start.py"]
