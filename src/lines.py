
from collections import deque


def check_liner_params(seed):
    if not isinstance(seed, (tuple, list, deque, str)):
        raise ValueError('seed have to be tuple, list, deque, or str')
    if not all(isinstance(s, int) or s in (' ', 'X') for s in seed):
        raise ValueError('seed must be int or "X  X XXX X"')
    if isinstance(seed, str):
        (*seed,) = (1 if s == 'X' else 0 for s in seed)
    if len(seed) < 0:
        raise ValueError('seed ca not be empty')
    return seed


def liner(automate, seed=(1,)):

    seed = check_liner_params(seed)
    seed_len = len(seed)

    def generator():
        try:
            l0, l1 = deque(seed), deque()
            if seed_len == 1:
                yield from _step_with_appender(_one_cell_appender, automate, l0, l1)
                l0, l1 = l1, deque()

            if seed_len == 2:
                yield from _step_with_appender(_two_cells_appender, automate, l0, l1)
                l0, l1 = l1, deque()

            while True:
                yield from _step_with_appender(_long_seed_appender, automate, l0, l1)
                l0, l1 = l1, deque()

        except InterruptedError:
            pass


    generator.__name__ = '{}_generator'.format(automate.__class__.__name__)
    return generator


def _step_with_appender(appender_func, automate, l0, l1):
    yield tuple(l0)
    appender_func(automate, l0, l1)


def _one_cell_appender(automate, l0, l1):
    x = l0.popleft()
    __append(automate, l1, 0, 0, x)
    __append(automate, l1, 0, x, 0)
    __append(automate, l1, x, 0, 0)


def _two_cells_appender(automate, l0, l1):
    x, y = l0.popleft(), l0.popleft()
    __append(automate, l1, 0, 0, x)
    __append(automate, l1, 0, x, y)
    __append(automate, l1, x, y, 0)
    __append(automate, l1, y, 0, 0)


def _long_seed_appender(automate, l0, l1):
    x, y, z = 0, 0, l0.popleft()
    __append(automate, l1, x, y, z)
    for base in range(0, len(l0)):
        x, y, z = y, z, l0.popleft()
        __append(automate, l1, x, y, z)
    __append(automate, l1, y, z, 0)
    __append(automate, l1, z, 0, 0)


def __append(automate, l, x, y, z):
    l.append(automate.next_step((x << 2) | (y << 1) | z))
