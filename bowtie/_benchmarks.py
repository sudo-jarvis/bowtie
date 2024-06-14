from __future__ import annotations

from pathlib import Path
from statistics import geometric_mean
from typing import TYPE_CHECKING, Any
import asyncio
import importlib
import json
import subprocess
import tempfile

from attrs import asdict, field, frozen
import pyperf  # type: ignore[reportMissingTypeStubs]

from bowtie import _connectables, _report
from bowtie._core import Dialect, Example, Test

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from bowtie._commands import (
        Message,
    )
    from bowtie._registry import ValidatorRegistry


def _get_benchmarks_from_file(file, module="bowtie.benchmarks") -> BenchmarkGroup | None:
    if file.suffix == ".py" and file.name != "__init__.py":
        benchmark_module_name = "." + file.stem
        data = importlib.import_module(
            benchmark_module_name,
            module,
        ).get_benchmark()
    elif file.suffix == ".json":
        data = json.loads(file.read_text())
    else:
        return None

    if isinstance(data, dict):
        benchmark = Benchmark.from_dict(
            **data,
        ).maybe_set_dialect_from_schema()
        benchmark_group = BenchmarkGroup(name=benchmark.name, description=benchmark.description, benchmarks=[benchmark])
        return benchmark_group
    elif isinstance(data, list):
        benchmarks = [
            Benchmark.from_dict(
                **benchmark,
            ).maybe_set_dialect_from_schema()
            for benchmark in data
        ]
        benchmark_group = BenchmarkGroup(name="", description="", benchmarks=benchmarks)
        return benchmark_group
    else:
        return None


@frozen
class Benchmark:
    description: str
    name: str
    schema: Any
    tests: Sequence[Example | Test]
    dialect: Dialect | None = None

    @classmethod
    def from_dict(
            cls,
            tests: Iterable[dict[str, Any]],
            name: str,
            **kwargs: Any,
    ):
        return cls(
            tests=[Example.from_dict(**test) for test in tests],
            name=name,
            **kwargs,
        )

    def serializable(self) -> Message:
        return asdict(
            self,
            filter=lambda _, v: v is not None,
        )

    def benchmark_with_diff_tests(self, tests: Sequence[Example | Test]):
        benchmark = self.serializable()
        benchmark["tests"] = tests
        return Benchmark(**benchmark)

    def maybe_set_dialect_from_schema(self):
        dialect_from_schema: str | None = (  # type: ignore[reportUnknownVariableType]
            self.schema.get("$schema")  # type: ignore[reportUnknownMemberType]
            if isinstance(self.schema, dict)
            else None
        )
        if not dialect_from_schema:
            return self

        benchmark = self.serializable()
        benchmark["dialect"] = Dialect.from_str(dialect_from_schema)  # type: ignore[reportUnknownArgumentType]
        return Benchmark.from_dict(**benchmark)


@frozen
class BenchmarkGroup:
    name: str
    description: str
    benchmarks: Sequence[Benchmark]


@frozen
class BenchmarkReport:
    pass
    # metadata: RunMetadata


@frozen
class Benchmarker:
    _benchmark_groups: Sequence[BenchmarkGroup] = field(alias="benchmark_groups")
    _num_processes: int = field(
        alias="processes",
    )
    _num_loops: int = field(
        alias="loops",
    )
    _num_warmups: int = field(
        alias="warmups",
    )
    _num_values: int = field(
        alias="values",
    )
    _quiet: bool = field(
        alias="quiet",
    )
    _report: BenchmarkReport = field(
        alias="report",
        default=BenchmarkReport(),
    )

    @classmethod
    def from_default_benchmarks(cls, **kwargs: Any):
        bowtie_dir = Path(__file__).parent
        benchmark_dir = bowtie_dir.joinpath("benchmarks").iterdir()
        benchmark_groups = []

        for file in benchmark_dir:
            benchmark_group = _get_benchmarks_from_file(file)
            if not benchmark_group:
                continue
            benchmark_groups.append(benchmark_group)

        return cls(benchmark_groups=benchmark_groups, **kwargs)

    @classmethod
    def for_keywords(cls, dialect: Dialect, **kwargs: Any):
        bowtie_dir = Path(__file__).parent
        keywords_benchmark_dir = bowtie_dir.joinpath("benchmarks").joinpath("keywords")
        dialect_keyword_benchmarks = keywords_benchmark_dir.joinpath(dialect.short_name).iterdir()

        module_name = f"bowtie.benchmarks.keywords.{dialect.short_name}"
        benchmark_groups = []

        for file in dialect_keyword_benchmarks:
            print(f"Loaded {file.stem}")
            benchmark_group = _get_benchmarks_from_file(file, module=module_name)
            if not benchmark_group:
                continue
            benchmark_groups.append(benchmark_group)

        return cls(benchmark_groups=benchmark_groups, **kwargs)

    @classmethod
    def from_input(
        cls,
        schema: Any,
        instances: Iterable[Any],
        description: str,
        **kwargs: Any,
    ):
        tests = [
            Example(description=str(idx), instance=each)
            for idx, each in enumerate(instances)
        ]
        benchmarks = [
            Benchmark(
                name=description,
                description=description,
                tests=tests,
                schema=schema,
            ),
        ]
        benchmark_group = BenchmarkGroup(name=description, description=description, benchmarks=benchmarks)
        return cls(benchmark_groups=[benchmark_group], **kwargs)

    async def start(
        self,
        connectables: Iterable[_connectables.Connectable],
        dialect: Dialect,
        registry: ValidatorRegistry[Any],
    ):
        connectables = [connectable for connectable in connectables]
        for benchmark_group in self._benchmark_groups:
            bench_suite_for_connectable: dict[str, pyperf.BenchmarkSuite] = {}
            for connectable in connectables:
                silent_reporter = _report.Reporter(
                    write=lambda **_: None,  # type: ignore[reportUnknownArgumentType]
                )
                async with connectable.connect(
                    reporter=silent_reporter,
                    registry=registry,
                ) as implementation:
                    supports_dialect = dialect in implementation.info.dialects

                if not supports_dialect:
                    print(f"{connectable.to_terse()} does not supports dialect {dialect.serializable()}")
                    continue

                if not self._quiet:
                    print(connectable.to_terse())
                    print()

                benchmark_results: list[pyperf.Benchmark] = []

                for benchmark in benchmark_group.benchmarks:
                    if benchmark.dialect and benchmark.dialect != dialect:
                        print(f"Skipping {benchmark.name} as it does not support dialect {dialect.serializable()}")
                        continue
                    tests = benchmark.tests
                    for test in tests:
                        benchmark_case = benchmark.benchmark_with_diff_tests(
                            tests=[test],
                        )
                        bench = await self._run_benchmark(
                            benchmark_case,
                            dialect,
                            connectable,
                        )
                        if bench:
                            benchmark_results.append(bench)
                if len(benchmark_results):
                    benchmark_suite = pyperf.BenchmarkSuite(
                        benchmarks=benchmark_results,
                    )
                    connectable_name = connectable.to_terse()
                    if connectable_name=="container:730fb7bf211d58d5aee81451b460cc9c24884b297d685fc9f431ee37ffa0cbbf":
                        connectable_name = "js-json-schema"
                    if connectable_name=="container:85c3335fbdb617b713fe780ae373bc51df6fad1db136d70b658c985eb866f9f0":
                        connectable_name = "java-json-schema"
                    if connectable_name=="container:c854f39e653586d5d5e8a20fd281ac3390d3d99c0ba161170d052eb35bb9c7c2":
                        connectable_name = "python-jsonschema"
                    bench_suite_for_connectable[
                        connectable_name
                    ] = benchmark_suite

                if not self._quiet:
                    print()

            bench_suite_for_connectable = self._sort_benchmark_suites(
                bench_suite_for_connectable,
            )
            await self._compare_benchmark_suites(bench_suite_for_connectable)

    async def _compare_benchmark_suites(
        self,
        bench_suite_for_connectable: dict[str, pyperf.BenchmarkSuite],
    ):
        with tempfile.TemporaryDirectory(
            delete=True,
        ) as tmp_dir_path:
            suite_dir = Path(tmp_dir_path)
            benchmark_suite_filenames: list[str] = []
            for (
                    connectable_name,
                    bench_suite,
            ) in bench_suite_for_connectable.items():
                bench_suite_tmp_filename = suite_dir.joinpath(
                    f"{connectable_name}.json",
                )
                bench_suite.dump(str(bench_suite_tmp_filename))  # type: ignore[reportUnknownMemberType]
                benchmark_suite_filenames.append(str(bench_suite_tmp_filename))

            await self._pyperf_compare_command(*benchmark_suite_filenames)

    async def _run_benchmark(
        self,
        benchmark: Benchmark,
        dialect: Dialect,
        connectable: _connectables.Connectable,
    ) -> Any:
        benchmark_name = f"{benchmark.name}::{benchmark.tests[0].description}"

        benchmark_dict = benchmark.serializable()
        benchmark_dict.pop("name")

        if "dialect" in benchmark_dict:
            benchmark_dict.pop("dialect")

        with tempfile.NamedTemporaryFile(
            delete=True,
        ) as fp:
            path = Path(fp.name)
            path.write_text(json.dumps(benchmark_dict))
            try:
                output = await self._pyperf_benchmark_command(
                    "bowtie", "run", "-i", connectable.to_terse(),
                    "-D", dialect.serializable(),
                    fp.name,
                    name=benchmark_name,
                )
            except:
                print("err")
                return None

        bench = pyperf.Benchmark.loads(output)  # type: ignore[reportUnknownArgumentType]
        if not self._quiet:
            print(f"Running Benchmark - {benchmark_name}")
        return bench  # type: ignore[reportUnknownVariableType]

    async def _run_subprocess(
        self,
        *cmd: str,
    ):
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return stdout, stderr

    async def _pyperf_benchmark_command(
        self,
        *benchmark_cmd: str,
        name: str,
    ):
        stdout_fd = "1"
        output, err = await self._run_subprocess(
            "pyperf", "command",
            "--pipe", stdout_fd,
            "--processes", str(self._num_processes),
            "--values", str(self._num_values),
            "--warmups", str(self._num_warmups),
            "--loops", str(self._num_loops),
            "--name", name,
            *benchmark_cmd,
        )
        if err:
            _, inner_err = await self._run_subprocess(
                *benchmark_cmd,
            )
            if inner_err:
                print(inner_err)
            else:
                print(err)
            raise Exception
        return output

    async def _pyperf_compare_command(self, *benchmark_suite_filenames: str):
        output, err = await self._run_subprocess(
            "pyperf", "compare_to",
            "--table",
            "--table-format", "md",
            *benchmark_suite_filenames,
        )
        if err:
            print(err)
        print(output.decode())

    @staticmethod
    def _sort_benchmark_suites(
        bench_suite_for_connectable: dict[str, pyperf.BenchmarkSuite],
    ) -> dict[str, pyperf.BenchmarkSuite]:

        def _geometric_mean_of_bench_suite(bench_suite: pyperf.BenchmarkSuite):
            means = [b.mean() for b in bench_suite.get_benchmarks()]  # type: ignore[reportUnknownVariableType]
            return geometric_mean(means)  # type: ignore[reportUnknownArgumentType]

        return dict(sorted(
            bench_suite_for_connectable.items(),
            key=lambda item: _geometric_mean_of_bench_suite(item[1]),
        ))
