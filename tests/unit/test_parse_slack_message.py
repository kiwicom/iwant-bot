from iwant_bot.iwant_process import IwantRequest
import iwant_bot.start

default = iwant_bot.start._default_duration
max_duration = iwant_bot.start._max_duration

# format: (text, activities, user_ids, time, behest)
messages = (
    ('', [], set([]), default, []),
    ('coffee', ['coffee', ], set([]), default, []),
    ('coffee coffee', ['coffee', ], set([]), default, []),
    ('coffee.', ['coffee', ], set([]), default, []),
    (' coffee.   ', ['coffee', ], set([]), default, []),
    ('coffee!', ['coffee', ], set([]), default, []),
    (' coffee!   ', ['coffee', ], set([]), default, []),
    (' coffee?', ['coffee', ], set([]), default, []),
    ('coffee?   ', ['coffee', ], set([]), default, []),
    (' coffee,', ['coffee', ], set([]), default, []),
    ('coffee,   ', ['coffee', ], set([]), default, []),
    ('the coffee', ['coffee', ], set([]), default, []),
    ('instant-coffee', ['coffee', ], set([]), default, []),
    ('coffee and', ['coffee', ], set([]), default, []),
    ('coffee-like', ['coffee', ], set([]), default, []),
    ('*coffee*', ['coffee', ], set([]), default, []),
    ('`coffee`', ['coffee', ], set([]), default, []),
    ('"coffee"', ['coffee', ], set([]), default, []),
    ("'coffee'", ['coffee', ], set([]), default, []),
    ('  (coffee;', ['coffee', ], set([]), default, []),
    ('[coffee]', ['coffee', ], set([]), default, []),
    ('{coffee`', ['coffee', ], set([]), default, []),
    ('#coffee$', ['coffee', ], set([]), default, []),
    ("&coffee%", ['coffee', ], set([]), default, []),

    ('coffee_', [], set([]), default, []),
    ('_coffee', [], set([]), default, []),
    ('coffeehouse', [], set([]), default, []),
    ('hypercoffee', [], set([]), default, []),
    ('coff-ee', [], set([]), default, []),
    ('coff_ee ', [], set([]), default, []),
    ('coff ee', [], set([]), default, []),


    ('list', [], set([]), default, ['list', ]),
    ('list list', [], set([]), default, ['list', ]),
    ('help', [], set([]), default, ['help', ]),
    # subscribe and unsubscribe are not prepared yet.
    # ('subscribe', [], set([]), default, ['subscribe', ]),
    # ('unsubscribe', [], set([]), default, ['unsubscribe', ]),
    # ('subscribe coffee', ['coffee', ], set([]), default, ['subscribe', ]),
    # ('unsubscribe coffee', ['coffee', ], set([]), default, ['unsubscribe', ]),

    ('coffee in 19 minutes', ['coffee', ], set([]), 19 * 60.0, []),
    ('coffee in 0 minutes', ['coffee', ], set([]), 0, []),
    ('coffee in 13minutes', ['coffee', ], set([]), 13 * 60.0, []),
    ('coffee in 20 min', ['coffee', ], set([]), 20 * 60.0, []),
    ('coffee in 21min', ['coffee', ], set([]), 21 * 60.0, []),
    ('coffee in 22 m', ['coffee', ], set([]), 22 * 60.0, []),
    ('coffee in 23m', ['coffee', ], set([]), 23 * 60.0, []),
    (' in 24 min coffee', ['coffee', ], set([]), 24 * 60.0, []),
    ('coffee in 1h', ['coffee', ], set([]), 60 * 60.0, []),
    ('coffee in 3 h', ['coffee', ], set([]), 180 * 60.0, []),
    ('coffee in 2 hours', ['coffee', ], set([]), 120 * 60.0, []),
    # ('coffee in 1d', ['coffee', ], set([]), min(max_duration, 24 * 3600.0), []),
    ('coffee in 2days', ['coffee', ], set([]), min(max_duration, 48 * 3600.0), []),

    ('coffee in 1h and 24m', ['coffee', ], set([]), 84 * 60.0, []),
    ('coffee in 1h 25m', ['coffee', ], set([]), 85 * 60.0, []),
    # ('coffee in 1:26', ['coffee', ], set([]), 86 * 60.0, []),           # same as 'at 1:26'
    # ('coffee in 1h27m', ['coffee', ], set([]), 87 * 60.0, []),          # needs space
    # ("coffee in 83'", ['coffee', ], set([]), 83 * 60.0, []),            # cannot use ' for minutes
    ('coffee and list in 13minutes', ['coffee', ], set([]), 13 * 60.0, ['list', ]),

    ('<@U1234|user>', [], set(['U1234', ]), default, []),
    ('<@W4A3B1|0.._s3.-.>', [], set(['W4A3B1', ]), default, []),
    ('<@W4A3B1|0.._s3.-.> in 33 min.', [], set(['W4A3B1', ]), 33 * 60.0, []),
    ('<@W4A3B1|0.._s3.-.> and <@U1234|user>', [], set(['W4A3B1', 'U1234']), default, []),
    ('<@U1234|user> and <@U1234|user>', [], set(['U1234']), default, []),
    ('<@W4A3B1|0.._s3.-.> channel <#C1234|general>', [], set(['W4A3B1', ]), default, []),

    ('coffee and list with <@U1234|user> invite <@W4A3B1|a.-._s> in 1h and 17 min.',
     ['coffee', ], set(['U1234', 'W4A3B1']), 77 * 60.0, ['list', ]),

    # Failing tests due to the time parser, presence of '.+/-' denote to days -> zero hh, mm, ss
    # ('. coffee', ['coffee', ], set([]), default, []),
    # ('coffee:', ['coffee', ], set([]), default, []),     # don't know what is problem
    # ('/ coffee', ['coffee', ], set([]), default, []),
    # ('+ coffee', ['coffee', ], set([]), default, []),
    # ('- coffee', ['coffee', ], set([]), default, []),

    # ('coffee during 20 min', ['coffee', ], set([]), 20 * 60.0, []),    # cannot parse 'during'
)


def test_parse_messages():
    for line in messages:
        test = IwantRequest(
            {'text': line[0]},
            iwant_bot.start._iwant_activities,
            iwant_bot.start._iwant_behest,
            iwant_bot.start._slack_user_pattern,
            iwant_bot.start._other_words,
            default,
            max_duration
        )
        print(line)
        assert test.data['activities'] == line[1]
        assert set(test.data['invite_users_id']) == line[2]
        assert round(test.data['action_duration']) == line[3]
        assert test.data['behests'] == line[4]
