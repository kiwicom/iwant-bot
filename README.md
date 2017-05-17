# iwant-bot
Slackbot project implemented by [Kiwi.com](Kiwi.com) interns

## WIP
- first internship crew started on this 21th April 2017
- MVP is going to be available at the end of May 2017

## How to set up

* Make sure you have `docker` and `docker-compose`.
* Run `docker-compose up`.
* Visit `http://localhost:8080` in your browser. Read the instructions and check out some GET requests!

### Local development set up

Slack has [Incoming](https://api.slack.com/incoming-webhooks) and
[Outgoing WebHooks](https://api.slack.com/custom-integrations/outgoing-webhooks) in custom integrations,
which can be turn on for selected channels and/or activate by key_words at the beginning of each message.
Slack kiwislackbot.slack.com is set up for key_words `repeat` or `whoami` in all channels.

* Incoming WebHook adds message to the channel from the POST request with JSON payload:
`curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' https://hooks.slack.com/services/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`
(_#bot-channel_)

* Outgoing WebHook sends messages with leading key_words `repeat` or `whoami` to
 each given URLs (https://kiwislackbot{1..4}.localtunnel.me).

* _iwant-bot_ app listens to port 8080, so run [localtunnel](https://localtunnel.github.io/www/)
`lt -p 8080 -s 'kiwislackbot{1..4}'` to connect Slack with _iwant-bot_ app at localhost.
You can check _iwant-bot_ locally
`curl -X POST --data "user_name=0&channel_id=1&channel_name=2&service_id=3&team_domain=4&team_id=5&text=6&timestamp=7&token=9&user_id=9" http://localhost:8080`.

## Corner cases

* If a problem occurs when generating the image because it was not possible to get some dependencies, it means that the `requirements.txt` file needs to be regenerated from `requirements.in`.
  You will need `pip-compile` tool (which is part of the `pip-tools` PyPi package) to do this.
  See `requirements.txt` for details on how to do it.
* If the container timezone doesn't match, [override](https://docs.docker.com/compose/extends/#multiple-compose-files) the value of the `timezone` build argument.
* Localtunnel subdomain `kiwislackbot1` can be occupied, try different number 2, 3, or 4.
* Localtunnel can have problem with out network (502 bad gateway)
* Localtunnel and `curl -X POST --data "..."` can have problem too,
`curl: (92) HTTP/2 stream 1 was not closed cleanly: REFUSED_STREAM (err 7)`
