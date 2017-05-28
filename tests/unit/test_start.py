from iwant_bot import start


def test_add():
    assert start.add_numbers(0, 0) == 0
    assert start.add_numbers(1, 1) == 2
