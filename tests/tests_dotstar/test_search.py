"""Tests for dotstar search functionality."""

import pytest
from dotstar import search, find_all, Pattern


def test_search_simple():
    data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
    assert search(data, "users.*.name") == ["Alice", "Bob"]


def test_search_nested():
    data = {
        "a": {"x": {"value": 1}},
        "b": {"x": {"value": 2}},
        "c": {"x": {"value": 3}}
    }
    assert sorted(search(data, "*.x.value")) == [1, 2, 3]


def test_search_mixed_types():
    data = {
        "items": [
            {"price": 10},
            {"price": 20},
            {"discount": 5}  # no price
        ]
    }
    assert search(data, "items.*.price") == [10, 20]


def test_find_all():
    data = {"users": [{"id": 1}, {"id": 2}]}
    results = find_all(data, "users.*.id")
    assert results == [("users.0.id", 1), ("users.1.id", 2)]


def test_pattern_basic():
    p = Pattern("users.*.email")
    data = {"users": [{"email": "a@test.com"}, {"email": "b@test.com"}]}
    assert p.search(data) == ["a@test.com", "b@test.com"]


def test_pattern_composition():
    users = Pattern("users.*")
    emails = users / "contact" / "email"
    assert str(emails) == "users.*.contact.email"


def test_empty_results():
    data = {"users": []}
    assert search(data, "users.*.name") == []
    assert find_all(data, "users.*.name") == []


def test_multiple_wildcards():
    data = {
        "regions": {
            "north": {"stores": [{"sales": 100}, {"sales": 200}]},
            "south": {"stores": [{"sales": 150}]}
        }
    }
    sales = search(data, "regions.*.stores.*.sales")
    assert sorted(sales) == [100, 150, 200]
