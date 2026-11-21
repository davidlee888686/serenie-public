from kernel.journal import KernelJournal


def test_journal_append():
    j = KernelJournal()
    entry = j.append("EVENT", {"x": 1})
    assert entry.monotonic_step == 1
    assert entry.event_type == "EVENT"
    assert entry.entry_id == "ENT-0001"
    assert len(entry.current_hash) == 64
