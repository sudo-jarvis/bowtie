from pathlib import Path
import json
import uuid

import pytest

from bowtie import _benchmarks
from bowtie._benchmarks import BenchmarkGroup
from bowtie._cli import EX
from bowtie._core import Dialect, TestCase
from bowtie._direct_connectable import Direct
from bowtie.tests.test_integration import bowtie

validators = Direct.from_id("python-jsonschema").registry()

benchmark_report_validator = validators.for_uri(
    "tag:bowtie.report,2024:benchmark_report",
)
benchmark_report_validated, benchmark_report_invalidated = (
    benchmark_report_validator.validated,
    benchmark_report_validator.invalidated,
)

benchmark_validator = validators.for_uri(
    "tag:bowtie.report,2024:benchmarks",
)
benchmark_validated, benchmark_invalidated = (
    benchmark_validator.validated,
    benchmark_validator.invalidated,
)

bowtie_dir = Path(__file__).parent.parent
default_benchmarks_dir = bowtie_dir / "benchmarks"
keyword_benchmarks_dir = bowtie_dir / "benchmarks/keywords"

DIRECT_CONNECTABLE = "python-jsonschema"


@pytest.fixture()
def valid_single_benchmark():
    from bowtie.tests.benchmarks import valid_single_benchmark

    return valid_single_benchmark.get_benchmark()


@pytest.fixture()
def valid_benchmark_group(valid_single_benchmark):
    from bowtie.tests.benchmarks import valid_benchmark_group

    return valid_benchmark_group.get_benchmark()


@pytest.fixture()
def invalid_benchmark():
    from bowtie.tests.benchmarks import invalid_benchmark

    return invalid_benchmark.get_benchmark()


@pytest.fixture()
def benchmarker_run_args():
    return {
        "runs": 1,
        "loops": 1,
        "warmups": 1,
        "values": 2,
    }


def _iterate_over_benchmark_dir(directory):
    if not directory.exists():
        return
    for file in directory.iterdir():
        if file.suffix in (".json", ".py") and file.name != "__init__.py":
            yield file


def _validate_benchmark_file(file, module):
    data = _benchmarks._load_benchmark_group_from_file(
        file,
        module,
    ).serializable()
    if data:
        benchmark_validated(data)


class TestBenchmarkFormat:

    def test_validate_single_benchmark(self, valid_single_benchmark):
        assert benchmark_validated(valid_single_benchmark.serializable())

    def test_validate_benchmark_group(self, valid_benchmark_group):
        assert benchmark_validated(valid_benchmark_group.serializable())

    @pytest.mark.parametrize(
        "benchmark_file",
        _iterate_over_benchmark_dir(default_benchmarks_dir),
        ids=lambda f: str(f),
    )
    def test_validate_default_benchmark_format(self, benchmark_file):
        benchmark_module = "bowtie.benchmarks"
        _validate_benchmark_file(benchmark_file, benchmark_module)

    @pytest.mark.parametrize(
        "benchmark_file",
        _iterate_over_benchmark_dir(default_benchmarks_dir / "keywords"),
        ids=lambda f: str(f),
    )
    def test_validate_keyword_benchmark_format(self, benchmark_file):
        benchmark_module = "bowtie.benchmarks.keywords"
        _validate_benchmark_file(benchmark_file, benchmark_module)


class TestLoadBenchmark:

    def test_benchmark_set_dialect(self, valid_single_benchmark):
        benchmark_json = valid_single_benchmark.serializable()
        benchmark_json["schema"]["$schema"] = Dialect.latest().serializable()
        benchmark_with_explicit_dialect = _benchmarks.Benchmark.from_dict(
            **benchmark_json,
        ).maybe_set_dialect_from_schema()
        assert benchmark_with_explicit_dialect.dialect == Dialect.latest()

    def test_load_benchmark_with_diff_tests(self, valid_single_benchmark):
        benchmark = valid_single_benchmark.benchmark_with_diff_tests(
            tests=valid_single_benchmark.tests * 10,
        )
        assert benchmark_validated(benchmark.serializable())

    def test_load_single_benchmark_group_from_dict(
        self,
        valid_single_benchmark,
    ):
        benchmark = valid_single_benchmark.serializable()
        benchmark["benchmark_type"] = "test"
        benchmark_group = BenchmarkGroup.from_dict(
            benchmark,
        )

        assert benchmark_validated(benchmark_group.serializable())

    def test_load_benchmark_group_from_dict(self, valid_benchmark_group):
        benchmark_json = valid_benchmark_group.serializable()
        benchmark_group = BenchmarkGroup.from_dict(
            benchmark_json,
            uri=valid_benchmark_group.uri,
        )

        serializable = benchmark_group.serializable()

        assert benchmark_validated(serializable)
        assert valid_benchmark_group.serializable() == serializable

    def test_load_single_benchmark_group_from_json(
        self,
        tmp_path,
        valid_single_benchmark,
    ):
        tmp_path = tmp_path / "test_file.json"
        single_benchmark_json = valid_single_benchmark.serializable()
        single_benchmark_json["benchmark_type"] = "test"
        tmp_path.write_text(json.dumps(single_benchmark_json))
        benchmark_group = BenchmarkGroup.from_file(tmp_path)
        assert benchmark_validated(benchmark_group.serializable())

    def test_load_benchmark_group_from_json(
        self,
        tmp_path,
        valid_benchmark_group,
    ):
        tmp_path = tmp_path / "test_file.json"

        benchmark_group_json = valid_benchmark_group.serializable()
        benchmark_group_json["uri"] = str(tmp_path.absolute().as_uri())
        tmp_path.write_text(json.dumps(benchmark_group_json))

        loaded_benchmark_group = BenchmarkGroup.from_file(tmp_path)

        assert loaded_benchmark_group.serializable() == benchmark_group_json
        assert benchmark_validated(loaded_benchmark_group.serializable())

    def test_load_benchmark_groups_from_folder(self):
        benchmark_groups = BenchmarkGroup.from_folder(
            Path(__file__).parent / "benchmarks",
            module="bowtie.tests.benchmarks",
        )
        valid_benchmarks_for_test = 3
        valid_count = 0

        for benchmark_group in benchmark_groups:
            assert benchmark_validated(benchmark_group.serializable())
            valid_count += 1

        assert valid_count == valid_benchmarks_for_test


class TestBenchmarker:

    def test_default_benchmarker(self, benchmarker_run_args):
        if not default_benchmarks_dir.exists():
            return
        _benchmarks.Benchmarker.from_default_benchmarks(**benchmarker_run_args)

    @pytest.mark.parametrize(
        "dialect",
        Dialect.known(),
        ids=lambda param: param.short_name,
    )
    def test_keywords_benchmarker(self, dialect, benchmarker_run_args):
        dialect_keyword_benchmarks_dir = (
            keyword_benchmarks_dir / dialect.short_name
        )

        if not dialect_keyword_benchmarks_dir.exists():
            return

        _benchmarks.Benchmarker.for_keywords(
            dialect,
            **benchmarker_run_args,
        )

    def test_test_cases_benchmarker(
        self,
        valid_single_benchmark,
        benchmarker_run_args,
    ):
        test_case = TestCase(
            description=valid_single_benchmark.description,
            schema=valid_single_benchmark.schema,
            tests=valid_single_benchmark.tests,
        )

        _benchmarks.Benchmarker.from_test_cases(
            [test_case],
            **benchmarker_run_args,
        )

    def test_input_benchmarker(
        self,
        valid_single_benchmark,
        benchmarker_run_args,
    ):
        _benchmarks.Benchmarker.from_input(
            valid_single_benchmark.serializable(),
            **benchmarker_run_args,
        )
