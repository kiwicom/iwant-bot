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
	&& (cd iwant-bot && python setup.py develop) \
	&& true

CMD [ "python", "python -m iwant_bot.start"]
