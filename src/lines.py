
from collections import deque
from src.automate import AutomateCache


class LinerMeta(type):

    __RUNNING_PLAN_DEF = {
        'direction': lambda d: d in ('+', '=', '-'),
        'automate': lambda a: isinstance(a, int) and 0 <= a <= 255,
        'lines': lambda l: isinstance(l, int) and l >= 0,
    }

    @classmethod
    def check_seed(mcs, seed):
        if not isinstance(seed, (tuple, list, deque, str)):
            raise ValueError('seed have to be tuple, list, deque, or str')
        if not all(isinstance(s, int) or s in (' ', 'X') for s in seed):
            raise ValueError('seed must be int or "X  X XXX X". Found : {}'.format(seed))
        if len(seed) < 0:
            raise ValueError('seed ca not be empty')
        if isinstance(seed, str):
            (*seed2,) = (1 if s == 'X' else 0 for s in seed)
            return seed2
        return tuple(seed)

    @classmethod
    def check_running_plan(mcs, running_plan):
        if not isinstance(running_plan, (tuple, list)):
            raise ValueError('running_plan have to be tuple or list')
        for inner_plan in running_plan:
            if not isinstance(inner_plan, dict):
                raise ValueError('every item in running_plan have to be dict')
            if not 0 == len(set(mcs.__RUNNING_PLAN_DEF.keys()) ^ set(inner_plan.keys())):
                raise KeyError('authorised and mandatory keys in running_plan item have to be {}'.format(
                    mcs.__RUNNING_PLAN_DEF.keys())
                )
            for key, value in inner_plan.items():
                test_lambda = mcs.__RUNNING_PLAN_DEF[key]
                if not test_lambda(value):
                    raise ValueError('value: {} of key: {} in running_plan item is not check compliant'.format(
                        value, key
                    ))

    @classmethod
    def _step_with_appender(mcs, appender_func, automate, l0, l1):
        yield tuple(l0)
        appender_func(automate, l0, l1)

    @classmethod
    def _append(mcs, automate, l, x, y, z):
        l.append(automate.next_step((x << 2) | (y << 1) | z))

    @classmethod
    def _ascending_one_cell_appender(mcs, automate, l0, l1):
        x = l0.popleft()
        mcs._append(automate, l1, 0, 0, x)
        mcs._append(automate, l1, 0, x, 0)
        mcs._append(automate, l1, x, 0, 0)

    @classmethod
    def _ascending_two_cells_appender(mcs, automate, l0, l1):
        x, y = l0.popleft(), l0.popleft()
        mcs._append(automate, l1, 0, 0, x)
        mcs._append(automate, l1, 0, x, y)
        mcs._append(automate, l1, x, y, 0)
        mcs._append(automate, l1, y, 0, 0)

    @classmethod
    def _ascending_long_seed_appender(mcs, automate, l0, l1):
        x, y, z = 0, 0, l0.popleft()
        mcs._append(automate, l1, x, y, z)
        for base in range(0, len(l0)):
            x, y, z = y, z, l0.popleft()
            mcs._append(automate, l1, x, y, z)
        mcs._append(automate, l1, y, z, 0)
        mcs._append(automate, l1, z, 0, 0)

    @classmethod
    def _constant_one_cell_appender(mcs, automate, l0, l1):
        x = l0.popleft()
        mcs._append(automate, l1, 0, x, 0)

    @classmethod
    def _constant_two_cells_appender(mcs, automate, l0, l1):
        x, y = l0.popleft(), l0.popleft()
        mcs._append(automate, l1, 0, x, y)
        mcs._append(automate, l1, x, y, 0)

    @classmethod
    def _constant_long_seed_appender(mcs, automate, l0, l1):
        x, y, z = 0, l0.popleft(), l0.popleft()
        mcs._append(automate, l1, x, y, z)
        for base in range(0, len(l0)):
            x, y, z = y, z, l0.popleft()
            mcs._append(automate, l1, x, y, z)
        mcs._append(automate, l1, y, z, 0)

    @classmethod
    def _descending_one_cell_appender(mcs, automate, l0, l1):
        _ = l0.popleft()

    @classmethod
    def _descending_two_cells_appender(mcs, automate, l0, l1):
        _, _ = l0.popleft(), l0.popleft()

    @classmethod
    def _descending_long_seed_appender(mcs, automate, l0, l1):
        x, y, z = l0.popleft(), l0.popleft(), l0.popleft()
        mcs._append(automate, l1, x, y, z)
        for base in range(0, len(l0)):
            x, y, z = y, z, l0.popleft()
            mcs._append(automate, l1, x, y, z)

    @classmethod
    def __ascending(mcs, automate, lines_count, l0, l1):
        if len(l0) == 1:
            yield from mcs._step_with_appender(mcs._ascending_one_cell_appender, automate, l0, l1)
            l0, l1 = l1, l0
            lines_count -= 1

        if len(l0) == 2:
            yield from mcs._step_with_appender(mcs._ascending_two_cells_appender, automate, l0, l1)
            lines_count -= 1

        while lines_count > 0:
            yield from mcs._step_with_appender(mcs._ascending_long_seed_appender, automate, l0, l1)
            l0, l1 = l1, l0
            lines_count -= 1

    @classmethod
    def __steadying(mcs, automate, lines_count, l0, l1):
        if len(l0) == 1:
            yield from mcs._step_with_appender(mcs._constant_one_cell_appender, automate, l0, l1)
            l0, l1 = l1, l0
            lines_count -= 1

        if len(l0) == 2:
            yield from mcs._step_with_appender(mcs._constant_two_cells_appender, automate, l0, l1)
            l0, l1 = l1, l0
            lines_count -= 1

        while lines_count > 0:
            yield from mcs._step_with_appender(mcs._constant_long_seed_appender, automate, l0, l1)
            l0, l1 = l1, l0
            lines_count -= 1

    @classmethod
    def __descending(mcs, automate, lines_count, l0, l1):
        if len(l0) == 1:
            yield from mcs._step_with_appender(mcs._descending_one_cell_appender, automate, l0, l1)
            l0, l1 = l1, l0
            lines_count -= 1

        if len(l0) == 2:
            yield from mcs._step_with_appender(mcs._descending_two_cells_appender, automate, l0, l1)
            l0, l1 = l1, l0
            lines_count -= 1

        while lines_count > 0:
            yield from mcs._step_with_appender(mcs._descending_long_seed_appender, automate, l0, l1)
            l0, l1 = l1, l0
            lines_count -= 1

    def __new__(mcs, name, bases, namespace, *_, running_plan=None, seed=(1,), **kwargs):
        mcs.check_running_plan(running_plan)
        checked_seed = mcs.check_seed(seed)
        cache = AutomateCache()

        namespace = dict(namespace)
        namespace.update(
            {
                '_seed': checked_seed,
                '_running_plan': running_plan,
                '_cache': cache,
            }
        )

        _executable_plans = []
        for one_plan in running_plan:
            direction = one_plan['direction']
            automate_instance = cache.get(one_plan['automate'])
            lines = one_plan['lines']
            if direction == '+':
                _executable_plans.append((mcs.__ascending, automate_instance, lines))
            if direction == '=':
                _executable_plans.append((mcs.__steadying, automate_instance, lines))
            if direction == '-':
                _executable_plans.append((mcs.__descending, automate_instance, lines))

        namespace.update(
            {
                '_executable_plans': _executable_plans,
                '_executable_plans_it': iter(_executable_plans),
                '_l0': deque(checked_seed),
                '_l1': deque(),
            }
        )

        def __iter__(self):
            try:
                while True:
                    nx_func, nx_automate, nx_lines = next(self._executable_plans_it)
                    yield from nx_func(nx_automate, nx_lines, self._l0, self._l1)
            except StopIteration:
                pass

        namespace.update({'__iter__': __iter__})

        return super().__new__(mcs, name, bases, dict(namespace))

    def __init__(cls, name, bases, namespace, *_, running_plan=None, seed=(1,), **kwargs):
        super().__init__(name, bases, dict(namespace))


def computed_plan(running_plan, seed):
    name = 'AutomatePlanExecutor'
    bases = (object,)
    namespace = {'metaclass': LinerMeta}
    custom_class_runner = LinerMeta(name, bases, namespace, running_plan=running_plan, seed=seed)
    return custom_class_runner()
