import json
import os

from noir.templating import templater


def test_env():
    assert templater._render(
        "{{ =env.get('HOME', '') }}", 'tenv'
    ) == os.environ.get("HOME", "")


_indent_in = """{
    "a": 1,
    "b": {{ =indent(data, 4) }}
}
"""
_indent_target = """{
    "a": 1,
    "b": {
        "c": 2
    }
}
"""


def test_indent():
    assert templater._render(
        _indent_in, 'tindent', context={"data": json.dumps({"c": 2}, indent=4)}
    ) == _indent_target


_tojson_in = """{
    "a": 1,
    "b": {{ =to_json(data) }}
}
"""
_tojson_target = """{
    "a": 1,
    "b": {"c": 2}
}
"""


def test_tojson():
    assert templater._render(
        _tojson_in, 'tjson', context={"data": {"c": 2}}
    ) == _tojson_target


_totoml_target = """[test]
a = 1
b = "foo"
"""


def test_totoml():
    assert templater._render(
       "{{ =to_toml(data) }}", 'ttoml', context={"data": {"test": {"a": 1, "b": "foo"}}}
    ) == _totoml_target


_toyaml_target = """test:
  a: 1
  b: foo
"""


def test_toyaml():
    assert templater._render(
       "{{ =to_yaml(data) }}", 'tyaml', context={"data": {"test": {"a": 1, "b": "foo"}}}
    ) == _toyaml_target
