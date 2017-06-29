import collections


class IgnoreList(object):
    def __init__(self):
        self._ignored_users = collections.defaultdict(list)

    def ignore(self, user, ignored):
        if ignored not in self._ignored_users[user]:
            self._ignored_users[user].append(ignored)

    def unignore(self, user, ignored):
        if ignored in self._ignored_users[user]:
            self._ignored_users[user].remove(ignored)

    def ignored_by_user(self, user):
        return self._ignored_users[user]

    def user_ignores(self, user, ignored):
        if ignored in self._ignored_users[user]:
            return True
        return False

    def is_ignoring_pair(self, user1, user2):
        if user2 in self._ignored_users[user1]:
            if user1 in self._ignored_users[user2]:
                return True
        return False

    def mutual_ignore_check(self, user1, user2):
        if user2 in self._ignored_users[user1]:
            return True
        elif user1 in self._ignored_users[user2]:
            return True
        return False
