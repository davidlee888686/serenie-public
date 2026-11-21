from kernel.evidence import create_evidence


def test_evidence_creation():
    ev = create_evidence("X", 1, "abc123", {})
    assert ev.contract_name == "Default_Evidence_Gate"
    assert ev.determinism_level == "D_4"
    assert ev.input_coordinate.startswith("X::1::")
    assert ev.output_coordinate.startswith("X::1::EXEC-")
    assert ev.evidence_id.startswith("EVID-")
    assert len(ev.evidence_id) >= 8
