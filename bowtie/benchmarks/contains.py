def get_benchmark():
    array_size = 1000
    beginning = [37] + [0] * (array_size - 1)
    middle = [0] * (array_size // 2) + [37] + [0] * (array_size // 2)
    end = [0] * (array_size - 1) + [37]
    invalid = [0] * array_size
    return dict(
        title="Contains Keyword",
        description=(
            "A benchmark for validation of the `contains` keyword."
        ),
        schema={
            "type": "array",
            "contains": {"const": 37},
        },
        cases=[
            dict(description="Empty array", case=[]),
            dict(description="Beginning of array", case=beginning),
            dict(description="Middle of array", case=middle),
            dict(description="End of array", case=end),
            dict(description="Invalid array", case=invalid),
        ],
    )
