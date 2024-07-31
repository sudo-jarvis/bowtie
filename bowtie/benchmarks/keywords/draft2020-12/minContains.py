from pathlib import Path
import uuid

from url.url import URL

from bowtie._benchmarks import Benchmark, BenchmarkGroup


def get_benchmark():

    name = "minContains"
    description = (
        "A benchmark for measuring performance of the implementation "
        "for the minContains keyword."
    )

    max_array_size = 100000
    array_size = 1000

    benchmarks = []
    while array_size <= max_array_size:
        array = [uuid.uuid4().hex for _ in range(array_size)]

        both_at_first = [1, 1] + array[:-2]
        both_at_middle = (
            array[1 : array_size // 2] + [1, 1] + array[array_size // 2 : -1]
        )
        both_at_last = array[:-2] + [1, 1]
        invalid = array

        tests = (
            [
                dict(description="Both at First", instance=both_at_first),
                dict(
                    description="Both at Middle",
                    instance=both_at_middle,
                ),
                dict(description="Both at Last", instance=both_at_last),
                dict(description="Invalid", instance=invalid),
            ]
            if array_size == max_array_size
            else [
                dict(
                    description="Both at Middle",
                    instance=both_at_middle,
                ),
            ]
        )

        benchmarks.append(
            Benchmark.from_dict(
                name=f"minContains_{array_size}",
                description=(
                    "A benchmark for validation of the `minContains` keyword."
                ),
                schema={
                    "type": "array",
                    "contains": {"type": "integer"},
                    "minContains": 2,
                },
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
