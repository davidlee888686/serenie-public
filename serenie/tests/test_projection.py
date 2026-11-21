import json

from kernel.projection import KernelProjectionEngine


def test_projection_views():
    p = KernelProjectionEngine()
    views = p.build_projection_views({"a": 1}, [{"x": 2}])
    assert json.loads(views["json_view"])["a"] == 1
    assert views["journal_block_count"] == 1
    assert "html_view" in views
    assert "markdown_view" in views
