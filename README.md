# iwant-bot
Slackbot project implemented by [Kiwi.com](Kiwi.com) interns

## WIP
- first internship crew started on this 21th April 2017
- MVP is going to be available at the end of May 2017

## How to set up

* Make sure you have `docker` and `docker-compose`.
* Run `docker-compose up`.
* Visit `http://localhost:8080` in your browser. Read the instructions and check out some GET requests!.

## Corner cases

* If a problem occurs when generating the image because it was not possible to get some dependencies, it means that the `requirements.txt` file needs to be regenerated from `requirements.in`.
  You will need `pip-compile` tool (which is part of the `pip-tools` PyPi package) to do this.
  See `requirements.txt` for details on how to do it.
