from datetime import datetime
from iwant_bot.slack_communicator import SlackCommunicator


async def notify_not_matched_request(store, time_proximity, bot_token):
    obsolete_results = store.get_requests_by_deadline_proximity(
        datetime.now(), time_proximity)
    users = []
    for result in obsolete_results:
        # currently, all requests are unmatched, due to missing matching logic.
        users.append(result.person_id)
    if len(users) > 0:
        slack = SlackCommunicator(bot_token, users, 'Sorry, nobody else was found for coffee.')
        await slack.send_message_to_each()
