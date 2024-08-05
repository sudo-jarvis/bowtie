from pathlib import Path

from url.url import URL

from bowtie._benchmarks import Benchmark, BenchmarkGroup


def get_benchmark():

    name = "contains"
    description = "A benchmark for validation of the `contains` keyword."

    max_array_size = 100000
    array_size = 1000

    benchmarks = []
    while array_size <= max_array_size:

        start = [37] + [0] * (array_size - 1)
        middle = [0] * (array_size // 2) + [37] + [0] * (array_size // 2)
        end = [0] * (array_size - 1) + [37]
        invalid = [0] * array_size

        tests = (
            [
                dict(description="Empty array", instance=[]),
                dict(description="Beginning of array", instance=start),
                dict(description="Middle of array", instance=middle),
                dict(description="End of array", instance=end),
                dict(description="Invalid array", instance=invalid),
            ]
            if array_size == max_array_size
            else [
                dict(description="Middle of array", instance=middle),
            ]
        )

        benchmarks.append(
            Benchmark.from_dict(
                name=f"Array Size - {array_size}",
                description=(
                    "Validating contains keyword over an array "
                    f"of size {array_size}"
                ),
                schema={
                    "type": "array",
                    "contains": {"const": 37},
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
