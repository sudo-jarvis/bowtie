def get_benchmark():
    num_useless_keywords = 100000

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
                *((str(i), i) for i in range(num_useless_keywords)),
                ("type", "integer"),
                *((str(i), i)
                  for i in range(num_useless_keywords, num_useless_keywords)),
                ("minimum", 37),
            ],
        ),
        cases=[
            dict(description="Beginning of schema", case=42),
            dict(description="Middle of schema", case="foo"),
            dict(description="End of schema", case=12),
            dict(description="Valid", case=3737),
        ],
    )
