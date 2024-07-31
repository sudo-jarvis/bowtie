from pathlib import Path
import uuid

from url.url import URL

from bowtie._benchmarks import Benchmark, BenchmarkGroup


def get_benchmark():
    name = "enum"
    description = (
        "A benchmark for measuring performance of the implementation "
        "for the enum keyword."
    )

    max_array_size = 100000
    array_size = 1000

    benchmarks = []
    while array_size <= max_array_size:
        array = [uuid.uuid4().hex for _ in range(array_size)]

        tests = (
            [
                dict(description="Valid First", instance=array[0]),
                dict(
                    description="Valid Middle",
                    instance=array[array_size // 2],
                ),
                dict(description="Valid Last", instance=array[-1]),
                dict(description="Invalid", instance=uuid.uuid4().hex),
            ]
            if array_size == max_array_size
            else [
                dict(description="Invalid", instance=uuid.uuid4().hex),
            ]
        )

        benchmarks.append(
            Benchmark.from_dict(
                name=f"Array Size - {array_size}",
                description=(
                    f"Validating the `enum` keyword over array of size {array_size}."
                ),
                schema=dict(enum=array),
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
