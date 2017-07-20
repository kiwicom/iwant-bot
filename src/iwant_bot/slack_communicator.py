import json
from aioslacker import Slacker


class SlackCommunicator(object):
    """Send message to Slack users, channels, and/or multiparty chats.
    Just specify 'user_id' and/or 'channel_id' (upper case letters and numbers).
    It can also create private channels and invite people,
    but for groups up to 7 people use multiparty chats (MPIM)."""

    bot_name = 'iwant-bot'

    def __init__(self, token, users, text: str = '', attachments: dict = None):
        if type(users) is str:
            self.users = [users]
        else:
            self.users = users
        self.text = text
        self.attachments = attachments
        self.token = token
        self.channel_id = None
        self.bot_id = None
        self.members = None

    async def get_users_dict(self) -> dict:
        async with Slacker(self.token) as slack:
            response = await slack.users.list()
        return {user['name']: user['id'] for user in response.body['members']}

    async def send_message_to_each(self, users: list = None):
        """Send message to each user and/or channel."""
        if users is None:
            users = self.users
        async with Slacker(self.token) as slack:
            for user in users:
                await slack.chat.post_message(channel=user,
                                              text=self.text,
                                              attachments=json.dumps(self.attachments))

    async def create_private_channel(self, channel_name: str) -> str:
        """Create private channel (group) and invite 'iwant-bot'.
        SUPER_TOKEN is needed for this action."""
        async with Slacker(self.token) as slack:
            response = await slack.groups.create(channel_name)
            self.channel_id = response.body['group']['id']
            print(f'Private channel <#{self.channel_id}|{channel_name}> was created.')

            # Once the bot is added into the group, just 'BOT_TOKEN' is sufficient for posting.
            if self.bot_id is None:
                self.bot_id = (await self.get_users_dict())[self.bot_name]

            await self.invite_people_in_private_channel(users=[self.bot_id])
            print(f"<@{self.bot_id}|iwant-bot> was added into the"
                  f" private channel <#{self.channel_id}|{channel_name}>.")
        return self.channel_id

    async def invite_people_in_private_channel(self, channel_id: str = None, users: list = None):
        """Invite people in the private channel (group). SUPER_TOKEN is needed."""
        if channel_id is None:
            channel_id = self.channel_id
        if users is None:
            users = self.users

        async with Slacker(self.token) as slack:
            res = await slack.groups.info(channel_id)
            members = res.body['group']['members']
            for user in users:
                if user not in members:
                    await slack.groups.invite(channel_id, user)
                    print(f'User {user} was added into the group {channel_id}.')

    async def send_message_to_multiparty(self):
        """Send message to Slack 'multiparty direct message'.
        Minimal 2 and maximal 8 participants."""
        async with Slacker(self.token) as slack:
            if self.bot_id is None:
                self.bot_id = (await self.get_users_dict())[self.bot_name]

            response = await slack.mpim.open(self.users + [self.bot_id])
            self.channel_id = response.body['group']['id']
            print(f"Message was send to multiparty chat {self.channel_id} to users:")
            print(', '.join(self.users))
            await self.send_message_to_each([self.channel_id])
