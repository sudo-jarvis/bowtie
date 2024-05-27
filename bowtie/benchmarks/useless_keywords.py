def get_benchmark():
    NUM_USELESS_KEYWORDS = 100000

    return dict(
        title="Useless Keywords",
        description=(
            "A benchmark for validation of schemas containing "
            "lots of useless keywords. "
            "Checks we filter them out once, ahead of time."
        ),
        schema=dict(
            [
                ("not", {"const": 42}),
                *((str(i), i) for i in range(NUM_USELESS_KEYWORDS)),
                ("type", "integer"),
                *((str(i), i)
                  for i in range(NUM_USELESS_KEYWORDS, NUM_USELESS_KEYWORDS)),
                ("minimum", 37),
            ],
        ),
        cases=[
            3737,
            12,
        ],
    )
