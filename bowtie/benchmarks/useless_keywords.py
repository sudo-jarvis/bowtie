from bowtie._benchmarks import Benchmark


def get_benchmark():
    num_useless_keywords = 300000

    return Benchmark.from_dict(
        name="useless_keywords",
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
                *(
                    (str(i), i)
                    for i in range(
                        num_useless_keywords,
                        num_useless_keywords,
                    )
                ),
                ("minimum", 37),
            ],
        ),
        tests=[
            dict(description="Beginning of schema", instance=42),
            dict(description="Middle of schema", instance="foo"),
            dict(description="End of schema", instance=12),
            dict(description="Valid", instance=3737),
        ],
    )
