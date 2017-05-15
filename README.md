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
which can be turn on for selected channels. It is set up for kiwislackbot.slack.com on _#bot-channel_.

* Incoming WebHook adds message to the channel from the POST request with JSON payload:
`curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' https://hooks.slack.com/services/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`
(_#bot-channel_)
* Outgoing WebHook sends POSTs to each given URLs. Messages from _bot-channel_ are sent to 
https://kiwislackbot{1..4}.localtunnel.me
* To route slack requests to a local _iwant-bot_ app, run [localtunnel](https://localtunnel.github.io/www/) 
`lt -p 8080 -s 'kiwislackbot{1..4}'`. _iwant-bot_ listens to the slack's POSTs, you can check it by command
`curl -X POST https://kiwislackbot{1..4}.localtunnel.me/`

## Corner cases

* If a problem occurs when generating the image because it was not possible to get some dependencies, it means that the `requirements.txt` file needs to be regenerated from `requirements.in`.
  You will need `pip-compile` tool (which is part of the `pip-tools` PyPi package) to do this.
  See `requirements.txt` for details on how to do it.
* If the container timezone doesn't match, [override](https://docs.docker.com/compose/extends/#multiple-compose-files) the value of the `timezone` build argument.
* Localtunnel subdomain `kiwislackbot1` can be occupied, try different number 2, 3, or 4.
