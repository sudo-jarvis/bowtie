from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import importlib, json
from typing import Any

from bowtie._core import TestCase, Example

BENCHMARKS_MODULE = "bowtie.benchmarks"


def get_default_benchmarks() -> Iterable[dict[str, Any]]:

    bowtie_dir = Path(__file__).parent
    benchmark_dir = bowtie_dir.joinpath("benchmarks").iterdir()

    for file in benchmark_dir:
        if file.suffix == ".py":
            benchmark_module_name = "." + file.stem
            benchmark = importlib.import_module(
                benchmark_module_name,
                BENCHMARKS_MODULE
            ).get_benchmark()
        elif file.suffix == ".json":
            benchmark = json.loads(file.read_text())
        else:
            continue

        yield benchmark

        tests = [Example(description="", instance=each) for each in benchmark['cases']]
        testcase = TestCase(
            description=benchmark['description'],
            schema=benchmark['schema'],
            tests=tests,
        )
        yield testcase
