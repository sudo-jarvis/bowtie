from itertools import cycle

def get_benchmark():
    return dict(
    title = "Nested Schemas",
    description = (
        "Validating highly nested schemas shouldn't "
        "cause exponential time blowups."
    ),
    schema = {
        "$id": "https://example.com/draft/2020-12/schema/strict",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$vocabulary": {
            "https://json-schema.org/draft/2020-12/vocab/core": True,
            "https://json-schema.org/draft/2020-12/vocab/applicator": True,
            "https://json-schema.org/draft/2020-12/vocab/unevaluated": True,
            "https://json-schema.org/draft/2020-12/vocab/validation": True,
            "https://json-schema.org/draft/2020-12/vocab/meta-data": True,
            "https://json-schema.org/draft/2020-12/vocab/format-annotation": True,
            "https://json-schema.org/draft/2020-12/vocab/content": True,
        },
        "$dynamicAnchor": "meta",
        "$ref": "https://json-schema.org/draft/2020-12/schema",
        "unevaluatedProperties": False,
    },
    cases = [
        nested_object(levels=levels) for levels in range(1, 11, 3)
    ],
    )

def nested_object(levels: int):
    """
    Produce a schema which validates deeply nested objects and arrays.
    """
    names = cycle(["foo", "bar", "baz", "quux", "spam", "eggs"])
    schema = {
        "type": "object",
        "properties": {"ham": {"type": "string"}},
    }
    for _, name in zip(range(levels - 1), names):
        schema = {"type": "object", "properties": {name: schema}}
    return schema
