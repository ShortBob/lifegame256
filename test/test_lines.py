
import pytest
from src.automate import AutomateCache
from src.lines import liner


def test_generator_name():
    automate_cache = AutomateCache()
    a121 = automate_cache.get(121)
    generator = liner(a121)
    assert generator.__name__ == 'Automate121_generator'
