from iwant_bot.ignore import IgnoreList


def make_ignore_list_filled():
    ignore_list = IgnoreList()
    ignore_list.ignore('Ivan', 'Michael')
    ignore_list.ignore('Ivan', 'Peter')
    ignore_list.ignore('Ivan', 'Franklin')
    ignore_list.ignore('Ivan', 'Joshua')
    ignore_list.ignore('Ivan', 'Michael')
    ignore_list.ignore('Ivan', 'Debora')
    ignore_list.ignore('Debora', 'Michael')
    ignore_list.ignore('Debora', 'Michelle')
    ignore_list.ignore('Debora', 'Marques')
    ignore_list.ignore('Debora', 'Ivan')
    return ignore_list


def test_ignore():
    ignore_list = make_ignore_list_filled()
    assert len(ignore_list.ignored_by_user('Ivan')) == 5
    assert len(ignore_list.ignored_by_user('Debora')) == 4
    ignore_list.unignore('Ivan', 'Peter')
    who = ignore_list.ignored_by_user('Ivan')
    assert who == ['Michael', 'Franklin', 'Joshua', 'Debora']
    assert not ignore_list.user_ignores('Debora', 'Joshua')
    assert ignore_list.user_ignores('Debora', 'Marques')


def test_ignoring_pair():
    ignore_list = make_ignore_list_filled()
    assert ignore_list.is_ignoring_pair('Ivan', 'Debora')
    assert not ignore_list.is_ignoring_pair('Debora', 'Marques')
