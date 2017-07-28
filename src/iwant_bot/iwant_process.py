from dateparser import parse
from datetime import datetime, timedelta
import re
import iwant_bot.pipeline


class IwantRequest(object):
    """Valid iwant command create this object, which extracts information with /iwant requests.
    Other_words are expected words in the user message, which should be removed before dateparse."""

    def __init__(self, body: dict, possible_activities: tuple, possible_behests: tuple,
                 user_pattern: str, other_words: tuple = (), default_duration: float = 900.0,
                 max_duration: float = None):

        self.possible_activities = possible_activities
        self.possible_behests = possible_behests
        self.default_duration = default_duration
        self.max_duration = max_duration

        self.data = body
        self.data['activities'] = get_words_present_in_text(body['text'], possible_activities)
        self.data['behests'] = get_words_present_in_text(body['text'], possible_behests)
        self.data['invite_users_id'] = get_unique_strings_matching_pattern(
            body['text'], user_pattern)
        date = parse_text_for_time(
            body['text'], user_pattern, possible_activities + possible_behests + other_words)

        if date is None:
            date = datetime.now() + timedelta(seconds=default_duration)

        self.data['deadline'] = date
        self.data['action_start'] = datetime.now()
        self.data['action_duration'] = (self.data['deadline']
                                        - self.data['action_start']).total_seconds()
        if max_duration is not None:
            self.data['action_duration'] = min(self.data['action_duration'], max_duration)
        if 'callback_id' not in self.data:
            self.data['callback_id'] = []

    def return_list_of_parameters(self) -> dict:
        text = 'Available activities are:\n`'\
               + '`\n`'.join(self.possible_activities) \
               + '`\nAvailable behests are:\n`'\
               + '`\n`'.join(self.possible_behests) + '`'
        return {'text': text}

    def store_iwant_task(self, activity) -> str:
        """Store to the database and get id -> Slack callback_id."""
        storage_object = iwant_bot.pipeline.pipeline.add_activity_request(
            self.data['user_id'], activity, self.data['deadline'],
            self.data['action_start'], self.data['action_duration']
        )
        return str(storage_object.id)

    def update_iwant_task(self, callback_id):
        pass

    def create_accepted_response(self) -> dict:
        """Create confirmation text and the cancel button."""
        text = (f"{', and '.join(self.data['activities'])}! "
                f"I am looking for someone for {round(self.data['action_duration'] / 60)} minutes.")
        attachment = [
            {
                'text': f"You can cancel {', '.join(self.data['activities'])}:",
                'callback_id': self.data['callback_id'],
                'fallback': 'This should be the cancel button.',
                'attachment_type': 'default',
                'actions': [
                    {
                        'name': 'Cancel',
                        'text': 'Cancel',
                        'type': 'button',
                        'value': '0'
                    }
                ]
            }
        ]
        return {'text': text, 'attachments': attachment}

    @staticmethod
    def create_help_message() -> dict:
        """Create help message for /iwant Slack command."""
        text = ('This is `/iwant help`.\n'
                'Use `/iwant activity` to let me know, what you want to do.'
                ' I will find someone, who will join you!\n'
                'You can get the list of available activities by `/iwant list`.\n'
                'Some examples:\n'
                '  `/iwant coffee`\n'
                '  `/iwant coffee in 35 min with @alex`'
                ' (I will notify @alex, but everyone can join.)\n'
                )
        return {'text': text}


def get_words_present_in_text(text: str, words: iter) -> list:
    """Search text for presence of whole given words."""
    return [word for word in words if
            re.search(fr'\b{word}\b', text)]


def get_unique_strings_matching_pattern(text: str, pattern: str) -> list:
    """Search text for e.g. names of users define by pattern."""
    return list(set(re.findall(pattern, text)))


def parse_text_for_time(text: str, user_pattern: str, words: iter) -> datetime or None:
    """Search text for duration of activities.
    Remove all other expected whole words and parse the rest.
    Note: time can contain symbols +-:./"""
    words_to_remove = r'\b{}\b'.format(r'\b|\b'.join(words))
    only_time_text = re.sub(rf'({user_pattern}|{words_to_remove}|'
                            r'''[][,;`*(){}"'!?\\]|'''
                            '\s*\.*\s*$)',
                            '', text)
    return parse(only_time_text)
