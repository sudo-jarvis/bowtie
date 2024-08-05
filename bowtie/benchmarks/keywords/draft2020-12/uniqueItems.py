from pathlib import Path

from url.url import URL

from bowtie._benchmarks import Benchmark, BenchmarkGroup


def get_benchmark():
    name = "uniqueItems"
    description = (
        "A benchmark for measuring performance of the "
        "implementation for the uniqueItems keyword."
    )
    max_array_size = 200000
    benchmarks = []

    array_size = 2000
    while array_size <= max_array_size:
        first_two_duplicate = [1, 1, *list(range(2, array_size - 2))]
        middle_two_duplicate = [
            *list(range(array_size // 2)),
            -1,
            -1,
            *list(range(array_size // 2, array_size)),
        ]
        last_two_duplicate = [*list(range(2, array_size - 2)), 1, 1]
        valid = list(range(array_size))

        tests = (
            [
                dict(
                    description="First Two Duplicate",
                    instance=first_two_duplicate,
                ),
                dict(
                    description="Middle Two Duplicate",
                    instance=middle_two_duplicate,
                ),
                dict(
                    description="Last Two Duplicate",
                    instance=last_two_duplicate,
                ),
                dict(description="Valid", instance=valid),
            ]
            if array_size == max_array_size
            else [
                dict(description="Valid", instance=valid),
            ]
        )

        benchmarks.append(
            Benchmark.from_dict(
                name=f"Array Size - {array_size}",
                description=(
                    f"Validating the `uniqueItems` keyword over array of size {array_size}."
                ),
                schema=dict(
                    uniqueItems=True,
                ),
                tests=tests,
            ),
        )

        array_size *= 10

    return BenchmarkGroup(
        name=name,
        description=description,
        benchmarks=benchmarks,
        uri=URL.parse(Path(__file__).absolute().as_uri()),
    )
