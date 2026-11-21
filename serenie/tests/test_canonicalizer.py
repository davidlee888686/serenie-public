from kernel.canonicalizer import Canonicalizer


def test_canonicalize_basic():
    c = Canonicalizer()
    result = c.canonicalize(b"Hello\r\nWorld  ")
    assert result == b"Hello\nWorld"
