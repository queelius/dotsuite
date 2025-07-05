"""Basic tests for dotget."""

import pytest
from dotget import get, exists, Path


def test_get_simple():
    data = {"a": {"b": "c"}}
    assert get(data, "a.b") == "c"


def test_get_with_index():
    data = {"items": ["first", "second", "third"]}
    assert get(data, "items.0") == "first"
    assert get(data, "items.1") == "second"


def test_get_with_default():
    data = {"a": 1}
    assert get(data, "b", "default") == "default"
    assert get(data, "a.b.c", 42) == 42


def test_exists():
    data = {"a": {"b": None}}
    assert exists(data, "a")
    assert exists(data, "a.b")
    assert not exists(data, "a.b.c")
    assert not exists(data, "x")


def test_path_basic():
    p = Path("a.b.c")
    assert str(p) == "a.b.c"
    assert repr(p) == "Path('a.b.c')"


def test_path_composition():
    base = Path("user")
    email = base / "email"
    assert str(email) == "user.email"

    deep = base / "settings" / "notifications" / "email"
    assert str(deep) == "user.settings.notifications.email"


def test_path_get():
    data = {"user": {"name": "Alice", "age": 30}}
    name_path = Path("user.name")
    age_path = Path("user.age")

    assert name_path.get(data) == "Alice"
    assert age_path.get(data) == 30
    assert Path("user.email").get(data, "none") == "none"
