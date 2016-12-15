
from src.automate import AutomateCache

__author__ = 'Vincent Farcette'


def test_automate_n_has_next_step_method():
    automate_cache = AutomateCache()
    a0 = automate_cache.get(0)
    assert 'next_step' in dir(a0), "Method AutomateN.next_step(...) is mandatory"


def test_automate_from_0_to_255_results():
    for rule in range(0, 2**8):
        automate_n = AutomateCache().get(rule_number=rule)
        found_rule = 0
        for i in range(0, 8):
            found_rule += automate_n.next_step(i) << i
        assert found_rule == rule, "The rule is {} but the found rule is {}...".format(rule, found_rule)
