# iwant-bot

[![Documentation Status](https://readthedocs.org/projects/iwantbot/badge/?version=latest)](http://iwantbot.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/kiwicom/iwant-bot/badge.svg?branch=master)](https://coveralls.io/github/kiwicom/iwant-bot?branch=master)

Slackbot project implemented by [Kiwi.com](Kiwi.com) interns.

The bot is supposed to collect requests of users, and notify those who have common requests and can therefore socially interact. So, for example, if Mary tells the bot at 9:00 that she wants to take a coffee break half-hour from now and Jack tells the bot the same at 9:10, the bot will notify them at some point that they can have the coffee together.

However, that's just the basic example, the bot can be used to perform much more things - check out the [use cases](use_cases.rst) to see more ideas!

## WIP
- first internship crew started on this 21th April 2017
- MVP is going to be available at the end of May 2017

## How to set up

* Make sure you have `docker` and `docker-compose`.
* Run `docker-compose up`.
* Visit `http://localhost:8080` in your browser. Read the instructions and check out some GET requests!

### Slack App sets up

Set up your [Slack App](https://api.slack.com/slack-apps) and connect it with your Slack Team. 
You will obtain a token for validation of incoming requests. Create a file `.env` in the repository and insert your tokens:
`BOT_TOKEN=xoxb-111111111111-a1A1a1A1a1A1a1A1a1A1a1A1`
`VERIFICATION=b2B2b2B2b2B2b2B2b2B2b2B2`, which are private.

* _iwant-bot_ server listens to port 8080, so run [localtunnel](https://localtunnel.github.io/www/)
or [ngrok](https://ngrok.com/) to create public adress, which you use in your Slack App. 

* Currently, the _iwant-bot_ server recognizes slash command `/iwant`.

* You can set up Incoming WebHook and send messages from _iwant-bot_ to the team channels.

* Still, you can check _iwant-bot_ locally
`curl -X POST --data "user_name=0&channel_name=1&text=2&token=3" http://localhost:8080`.

## Corner cases

* If a problem occurs when generating the image because it was not possible to get some dependencies,
 it means that the `requirements.txt` file needs to be regenerated from `requirements.in`.
  See `requirements.txt` for details on how to do it.
* If the container timezone doesn't match, [override](https://docs.docker.com/compose/extends/#multiple-compose-files) the value of the `timezone` build argument.
* Localtunnel can have problem with out network (502 bad gateway) and it is not stable, but you can define subdomain like `myslackbot.localtunnel.me`.
* Ngrok tunnel subdomain is paid.
* Do not forget to invite your bot to the channels.

