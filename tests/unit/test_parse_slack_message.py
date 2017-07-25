from iwant_bot.iwant_process import IwantRequest
import iwant_bot.start

default = iwant_bot.start._default_duration
max_duration = iwant_bot.start._max_duration

# format: (text, activities, user_ids, time, behest)
messages = (
    ('', [], [], default, []),
    ('coffee', ['coffee', ], [], default, []),
    ('coffee.', ['coffee', ], [], default, []),
    (' coffee.   ', ['coffee', ], [], default, []),
    ('coffee!', ['coffee', ], [], default, []),
    (' coffee!   ', ['coffee', ], [], default, []),
    (' coffee?', ['coffee', ], [], default, []),
    ('coffee?   ', ['coffee', ], [], default, []),
    (' coffee,', ['coffee', ], [], default, []),
    ('coffee,   ', ['coffee', ], [], default, []),
    ('the coffee', ['coffee', ], [], default, []),
    ('instant-coffee', ['coffee', ], [], default, []),
    ('coffee and', ['coffee', ], [], default, []),
    ('coffee-like', ['coffee', ], [], default, []),
    ('*coffee*', ['coffee', ], [], default, []),
    ('`coffee`', ['coffee', ], [], default, []),
    ('"coffee"', ['coffee', ], [], default, []),
    ("'coffee'", ['coffee', ], [], default, []),
    ('  (coffee;', ['coffee', ], [], default, []),
    ('[coffee]', ['coffee', ], [], default, []),
    ('{coffee`', ['coffee', ], [], default, []),
    ('#coffee$', ['coffee', ], [], default, []),
    ("&coffee%", ['coffee', ], [], default, []),

    ('coffee_', [], [], default, []),
    ('_coffee', [], [], default, []),
    ('coffeehouse', [], [], default, []),
    ('hypercoffee', [], [], default, []),
    ('coff-ee', [], [], default, []),
    ('coff_ee ', [], [], default, []),
    ('coff ee', [], [], default, []),


    ('list', [], [], default, ['list', ]),
    ('subscribe', [], [], default, ['subscribe', ]),
    ('unsubscribe', [], [], default, ['unsubscribe', ]),
    ('subscribe coffee', ['coffee', ], [], default, ['subscribe', ]),
    ('unsubscribe coffee', ['coffee', ], [], default, ['unsubscribe', ]),

    ('coffee in 19 minutes', ['coffee', ], [], 19 * 60.0, []),
    ('coffee in 0 minutes', ['coffee', ], [], 0, []),
    ('coffee in 13minutes', ['coffee', ], [], 13 * 60.0, []),
    ('coffee in 20 min', ['coffee', ], [], 20 * 60.0, []),
    ('coffee in 21min', ['coffee', ], [], 21 * 60.0, []),
    ('coffee in 22 m', ['coffee', ], [], 22 * 60.0, []),
    ('coffee in 23m', ['coffee', ], [], 23 * 60.0, []),
    (' in 24 min coffee', ['coffee', ], [], 24 * 60.0, []),
    ('coffee in 1h', ['coffee', ], [], 60 * 60.0, []),
    ('coffee in 3 h', ['coffee', ], [], 180 * 60.0, []),
    ('coffee in 2 hours', ['coffee', ], [], 120 * 60.0, []),
    # ('coffee in 1d', ['coffee', ], [], min(max_duration, 24 * 3600.0), []),
    ('coffee in 2days', ['coffee', ], [], min(max_duration, 48 * 3600.0), []),

    ('coffee in 1h and 24m', ['coffee', ], [], 84 * 60.0, []),
    ('coffee in 1h 25m', ['coffee', ], [], 85 * 60.0, []),
    # ('coffee in 1:26', ['coffee', ], [], 86 * 60.0, []),           # same as 'at 1:26'
    # ('coffee in 1h27m', ['coffee', ], [], 87 * 60.0, []),          # needs space
    # ("coffee in 83'", ['coffee', ], [], 83 * 60.0, []),            # cannot use ' for minutes
    ('coffee and list in 13minutes', ['coffee', ], [], 13 * 60.0, ['list', ]),

    ('<@U1234|user>', [], ['U1234', ], default, []),
    ('<@W4A3B1|0.._s3.-.>', [], ['W4A3B1', ], default, []),
    ('<@W4A3B1|0.._s3.-.> in 33 min.', [], ['W4A3B1', ], 33 * 60.0, []),
    ('<@W4A3B1|0.._s3.-.> and <@U1234|user>', [], ['W4A3B1', 'U1234'], default, []),
    ('<@W4A3B1|0.._s3.-.> channel <#C1234|general>', [], ['W4A3B1', ], default, []),

    ('coffee and list with <@U1234|user> invite <@W4A3B1|a.-._s> in 1h and 17 min.',
     ['coffee', ], ['U1234', 'W4A3B1'], 77 * 60.0, ['list', ]),

    # Failing tests due to the time parser, presence of '.+/-' denote to days -> zero hh, mm, ss
    # ('. coffee', ['coffee', ], [], default, []),
    # ('coffee:', ['coffee', ], [], default, []),     # don't know what is problem
    # ('/ coffee', ['coffee', ], [], default, []),
    # ('+ coffee', ['coffee', ], [], default, []),
    # ('- coffee', ['coffee', ], [], default, []),

    # ('coffee during 20 min', ['coffee', ], [], 20 * 60.0, []),    # cannot parse 'during'
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
        assert test.data['invite_users_id'] == line[2]
        assert round(test.data['action_duration']) == line[3]
        assert test.data['behests'] == line[4]
