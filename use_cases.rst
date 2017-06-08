Iwant bot use cases
===================

iwant coffee
------------

* Request is remembered.
* Duplicate requests are noticed and handled.
* We wait for another coffee request.
* Match the requests.
* Notify matched people.
* If many people want to follow an event, match them using a strategy (e.g. not the same people all of the time).
* Make it possible to cancel a request.

iwant something
---------------

* Same as coffee, but we have to determine how many people to connect.
* Number of persons could be specify in the request (as a number, range, whatever).
* Hierarchy of activities => general activities vs concrete ones (I want to drink something -> then you will drink coffee).
* Have a list of all available activities.
* List of activities (may be initially hardcoded, but it) should be possible to expand it by user's activities.

iwant something but I am late
-----------------------------

* When a group of people has been notified and another request appears shortly afterwards, tell "go now, maybe you will catch them".

iwant something but I can't join
--------------------------------

* Some activities are capacity-limited (game for four can't be played by ten people).

iwanttalk about an activity
---------------------------

* People that would like to participate in an activity should be able to communicate with each other easily.

ihate somebody, ilove somebody
------------------------------

* There should be possibility not to pair people that hate each other (and vice versa).
* Support personal preferences.

recognize patterns
------------------

* When a bot user makes pattern, remind the user if he doesn't follow it / assume that the user will follow it / tell the user only if somebody would like to follow the pattern.

educate the user
----------------

* Observer user's behavior, notify it if they seem to be unaware of some functionality of the bot.

fake messages
-------------

* Tell people that there is somebody wanting to go for (coffee), although there is nobody (but we hope that others will join, so there will be a group at the end).

scalability
-----------

* If multiple instances of the app are running, all requests should be treated globally, i.e. regardless of to which instance a request was submitted.
