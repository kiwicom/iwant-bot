from dateparser import parse
from datetime import datetime
import re


class IwantParser(object):
    """Valid iwant command should create this object."""

    _default_duration = 900.0  # Implicit duration of activity in seconds.
    _max_duration = 43200.0  # 12 hours is maximal duration of any request.

    def __init__(self, body: dict, possible_activities: tuple, possible_behests: tuple):

        self.possible_activities = possible_activities
        self.possible_behests = possible_behests
        slack_user_pattern = '<@([A-Z0-9]+)\|[a-z0-9][-_.a-z0-9]{1,20}>'

        self.data = body
        self.data['activities'] = self._parse_message_for_words(self.possible_activities)
        self.data['behests'] = self._parse_message_for_words(self.possible_behests)
        self.data['invite_users_id'] = self._parse_message_for_people(slack_user_pattern)
        self.data['deadline_ts'] = (self.data['incoming_ts']
                                    + self._parse_message_for_time(slack_user_pattern))
        self.data['duration_minutes'] = round(
            (self.data['deadline_ts'] - self.data['incoming_ts']) / 60
        )

    # async
    def create_iwant_task(self) -> bool:
        """Hand self over to database and get database id -> Slack callback_id."""
        if 'callback_id' not in self.data:
            # self.data['callback_id'] = await save_to_the_storage(self.data)
            self.data['callback_id'] = 'id-1234'
            if self.data['callback_id'] is not None:
                return True
            else:
                return False
        else:
            # upgrade task with callback_id
            # return await upgrade_storage_task(self.data)  -> True or False
            print('upgrading message...')
            return True

    def _parse_message_for_words(self, words: iter) -> list:
        """Search text for whole given words."""
        return [word for word in words if
                re.search(f'(^|\W){word}($|\W)', self.data['text'])]

    def _parse_message_for_people(self, pattern) -> list:
        """Search text for names to be invite to activity.
        Expect expanded Slack format like <@U1234|user> <#C1234|general>.
        Turn on 'Escape channels, users, and links sent to your app'
        for all Slack commands."""
        return re.findall(pattern, self.data['text'])

    def _parse_message_for_time(self, user_pattern) -> float:
        """Search text for duration of activities.
        Remove all other expected text and parse the rest.
        Time formats can contain +-:./
        Activity duration has default (15 min) and maximum value 12h."""
        text_only_time = re.sub(f'({"|".join(self.possible_activities)}|'
                                f'{"|".join(self.possible_behests)}|{user_pattern}'
                                '|iwant|with|invite|or|and|[][,;`*(){}"\'\\\!?]|\s*\.*\s*$)',
                                '', self.data['text'])
        deadline = parse(text_only_time)
        if deadline is None:
            return self._default_duration
        else:
            return min(max((deadline - datetime.now()).total_seconds(), 1.0), self._max_duration)

    def create_accepted_response(self) -> dict:
        """Create confirmation text and the cancel button."""
        text = (f"{', '.join(self.data['activities'])}!"
                f" I am looking for someone for {self.data['duration_minutes']} minutes.")
        attachment = [
            {
                'text': f"If you do not want {', '.join(self.data['activities'])} anymore,"
                        " you can cancel it.",
                'callback_id': f"{self.data['callback_id']}",
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

    def return_list_of_parameters(self) -> dict:
        text = 'Available activities are:\n`'
        text += '`\n`'.join(self.possible_activities)
        text += '`\nAvailable behests are:\n`'
        text += '`\n`'.join(self.possible_behests) + '`'
        return {'text': text}
