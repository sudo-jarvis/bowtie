from bowtie._core import validator_registry
from bowtie._benchmarks import get_default_benchmarks

validator = validator_registry().for_uri(
    "tag:bowtie.report,2024:connectables",
)


def validate_benchmarks_format():
    default_benchmarks = get_default_benchmarks()
    for benchmark in default_benchmarks:
        validator.validate(benchmark)
