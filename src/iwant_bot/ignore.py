import collections


class IgnoreList(object):
    def __init__(self):
        self.ignored_users = collections.defaultdict(list)

    def ignore(self, user, ignored):
        if ignored not in self.ignored_users[user]:
            self.ignored_users[user].append(ignored)

    def unignore(self, user, ignored):
        if ignored in self.ignored_users[user]:
            self.ignored_users[user].remove(ignored)

    def who(self, user):
        return self.ignored_users[user]

    def is_ignored(self, user, ignored):
        if ignored in self.ignored_users[user]:
            return True
        elif user in self.ignored_users[ignored]:
            return True
