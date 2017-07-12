Top-level documentation
=======================

The slackbot accepts requests from users that want to do something and that would like not to be alone when doing them.

For example, Alice can tell the bot that she would like to have a coffee with somebody from 10:00, but she needs to know whether anyone is going to join her at 9:30 latest (otherwise she might decide not to have a coffee at all).
Then, if Bob tells the bot at 9:20 that he would like to have a coffee during the next hour, the bot should put the two requests together.
This means telling Bob that he joins Alice at 10:00 and telling Alice that she can have coffee with Bob.

Terminology
-----------

Request is defined by

* user who placed it,
* activity that is being requested,
* deadline --- time the bot has to pair the user.
* activity start --- the time in which the activity is supposed to start.

Request resolution
------------------

#. The actual request is received via Slack (or other means).
#. It is parsed by the Slack backend and passed into request preprocessing pipeline.
#. In the pipeline, the request is
   
   * given an ID,
   * saved to a central database, and
   * task is dispatched for the worker.

Then comes the task worker:

#. The worker pulls stuff from the tasks queue.
#. According to what tasks arrive, it queries the requests database and updates it and saves stuff into the results database.

Finally, there needs to be a notification service that ensures that actors are notified at the right time (i.e. they are not spammed with notification that become obsolete soon).
