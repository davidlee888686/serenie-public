from kernel.delta import DeltaEngine


def test_delta_none():
    d = DeltaEngine()
    result = d.compare({"a": 1}, {"a": 1})
    assert result.has_changes is False
    assert result.added == {}
    assert result.removed == {}
    assert result.modified == {}


def test_delta_update():
    d = DeltaEngine()
    result = d.compare({"a": 1}, {"a": 2})
    assert result.has_changes is True
    assert result.modified["a"] == (1, 2)
