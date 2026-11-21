from kernel.replay import KernelReplayEngine


def test_replay_sequence():
    r = KernelReplayEngine()
    entries = [{"event": "A"}, {"event": "B"}]
    result = r.replay_journal_sequence(entries)
    assert result["replayed_blocks"] == 2
    assert result["status"] == "VERIFIED"
