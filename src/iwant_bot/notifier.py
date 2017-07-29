from datetime import datetime
from iwant_bot.slack_communicator import SlackCommunicator
from iwant_bot.start import BOT_TOKEN


def notify_not_matched_request(store):
    obsolete_results = store.get_requests_by_deadline_proximity(datetime.now(), 30)
    users = []
    for result in obsolete_results:
        # currently, all requests are unmatched, due to missing matching logic.
        users.append(result.person_id)
    if len(users) > 0:
        slack = SlackCommunicator(BOT_TOKEN, users, 'Sorry, nobody else was found for coffee.')
        slack.send_message_to_each()
