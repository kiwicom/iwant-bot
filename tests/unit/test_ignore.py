from iwant_bot.ignore import IgnoreList


def test_ignore():
    users = IgnoreList()
    users.ignore('Ivan', 'Michael')
    users.ignore('Ivan', 'Peter')
    users.ignore('Ivan', 'Franklin')
    users.ignore('Ivan', 'Joshua')
    users.ignore('Ivan', 'Michael')
    users.ignore('Debora', 'Michael')
    users.ignore('Debora', 'Michelle')
    users.ignore('Debora', 'Marques')
    assert len(users.ignored_users['Ivan']) == 4
    assert len(users.ignored_users['Debora']) == 3
    users.unignore('Ivan', 'Peter')
    who = users.who('Ivan')
    assert who == ['Michael', 'Franklin', 'Joshua']
    assert not users.is_ignored('Debora', 'Joshua')
    assert users.is_ignored('Debora', 'Marques')
