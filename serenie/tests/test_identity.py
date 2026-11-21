from kernel.identity import compute_identity


def test_identity_hash():
    ident = compute_identity("X", 1, b"data")
    assert ident.logical_id == "X"
    assert ident.version_id == 1
    assert ident.content_hash.startswith("sha256:")
    digest = ident.content_hash.removeprefix("sha256:")
    assert len(digest) == 64
