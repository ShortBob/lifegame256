
from collections import deque
from src.automate import AutomateCache


class Liner(object):

    __RUNNING_PLAN_DEF = {
        'direction': lambda d: d in ('+', '=', '-'),
        'automate': lambda a: isinstance(a, int) and 0 <= a <= 255,
        'lines': lambda l: isinstance(l, int) and l >= 0,
    }

    @classmethod
    def check_seed(cls, seed):
        if not isinstance(seed, (tuple, list, deque, str)):
            raise ValueError('seed have to be tuple, list, deque, or str')
        if not all(isinstance(s, int) or s in (' ', 'X') for s in seed):
            raise ValueError('seed must be int or "X  X XXX X"')
        if len(seed) < 0:
            raise ValueError('seed ca not be empty')
        if isinstance(seed, str):
            (*seed2,) = (1 if s == 'X' else 0 for s in seed)
            return seed2
        return seed

    @classmethod
    def check_running_plan(cls, running_plan):
        if not isinstance(running_plan, (tuple, list)):
            raise ValueError('running_plan have to be tuple or list')
        for inner_plan in running_plan:
            if not isinstance(inner_plan, dict):
                raise ValueError('every item in running_plan have to be dict')
            if not 0 == len(set(cls.__RUNNING_PLAN_DEF.keys()) ^ set(inner_plan.keys())):
                raise KeyError('authorised and mandatory keys in running_plan item have to be {}'.format(
                    cls.__RUNNING_PLAN_DEF.keys())
                )
            for key, value in inner_plan.items():
                test_lambda = cls.__RUNNING_PLAN_DEF[key]
                if not test_lambda(value):
                    raise ValueError('value: {} of key: {} in running_plan item is not check compliant'.format(
                        value, key
                    ))

    def __init__(self, running_plan, seed=(1,)):
        self._seed = self.__class__.check_seed(seed)
        self._running_plan = self.__class__.check_running_plan(running_plan)
        self._cache = AutomateCache()

        seed_ = self._seed
        running_plan_ = self._running_plan
        step_with_appender = self.__class__._step_with_appender
        asc_one_cell_appender = self.__class__._ascending_one_cell_appender
        asc_two_cells_appender = self.__class__._ascending_two_cells_appender
        asc_general_appender = self.__class__._ascending_long_seed_appender
        cst_one_cell_appender = self.__class__._constant_one_cell_appender
        cst_two_cells_appender = self.__class__._constant_two_cells_appender
        cst_general_appender = self.__class__._constant_long_seed_appender
        dsc_one_cell_appender = self.__class__._descending_one_cell_appender
        dsc_two_cells_appender = self.__class__._descending_two_cells_appender
        dsc_general_appender = self.__class__._descending_long_seed_appender
        automate_cache = self._cache.get

        def iterator(_running_plan):
            print("Iterator")
            l0, l1 = deque(seed_), deque()
            try:
                for one_plan in running_plan_:
                    print('InnerPlan : {}'.format(one_plan))
                    direction = one_plan['direction']
                    automate = automate_cache(one_plan['automate'])
                    lines = one_plan['lines']
                    if direction == '+':
                        if len(l0) == 1:
                            yield from step_with_appender(asc_one_cell_appender, automate, l0, l1)
                            l0, l1 = l1, deque()
                            lines -= 1

                        if len(l0) == 2:
                            yield from step_with_appender(asc_two_cells_appender, automate, l0, l1)
                            l0, l1 = l1, deque()
                            lines -= 1

                        while lines > 0:
                            yield from step_with_appender(asc_general_appender, automate, l0, l1)
                            l0, l1 = l1, deque()
                            lines -= 1

                    elif direction == '=':
                        if len(l0) == 1:
                            yield from step_with_appender(cst_one_cell_appender, automate, l0, l1)
                            l0, l1 = l1, deque()
                            lines -= 1

                        if len(l0) == 2:
                            yield from step_with_appender(cst_two_cells_appender, automate, l0, l1)
                            l0, l1 = l1, deque()
                            lines -= 1

                        while lines > 0:
                            yield from step_with_appender(cst_general_appender, automate, l0, l1)
                            l0, l1 = l1, deque()
                            lines -= 1

                    elif direction == '-':
                        if len(l0) == 1:
                            yield from step_with_appender(dsc_one_cell_appender, automate, l0, l1)
                            l0, l1 = l1, deque()
                            lines -= 1

                        if len(l0) == 2:
                            yield from step_with_appender(dsc_two_cells_appender, automate, l0, l1)
                            l0, l1 = l1, deque()
                            lines -= 1

                        while lines > 0:
                            yield from step_with_appender(dsc_general_appender, automate, l0, l1)
                            l0, l1 = l1, deque()
                            lines -= 1

            except InterruptedError:
                pass

        self._iterator = iterator

    def generator(self):
        return self._iterator

    @classmethod
    def _step_with_appender(cls, appender_func, automate, l0, l1):
        yield tuple(l0)
        appender_func(automate, l0, l1)

    @classmethod
    def _ascending_one_cell_appender(cls, automate, l0, l1):
        x = l0.popleft()
        cls.__append(automate, l1, 0, 0, x)
        cls.__append(automate, l1, 0, x, 0)
        cls.__append(automate, l1, x, 0, 0)

    @classmethod
    def _ascending_two_cells_appender(cls, automate, l0, l1):
        x, y = l0.popleft(), l0.popleft()
        cls.__append(automate, l1, 0, 0, x)
        cls.__append(automate, l1, 0, x, y)
        cls.__append(automate, l1, x, y, 0)
        cls.__append(automate, l1, y, 0, 0)

    @classmethod
    def _ascending_long_seed_appender(cls, automate, l0, l1):
        x, y, z = 0, 0, l0.popleft()
        cls.__append(automate, l1, x, y, z)
        for base in range(0, len(l0)):
            x, y, z = y, z, l0.popleft()
            cls.__append(automate, l1, x, y, z)
        cls.__append(automate, l1, y, z, 0)
        cls.__append(automate, l1, z, 0, 0)

    @classmethod
    def _constant_one_cell_appender(cls, automate, l0, l1):
        x = l0.popleft()
        cls.__append(automate, l1, 0, x, 0)

    @classmethod
    def _constant_two_cells_appender(cls, automate, l0, l1):
        x, y = l0.popleft(), l0.popleft()
        cls.__append(automate, l1, 0, x, y)
        cls.__append(automate, l1, x, y, 0)

    @classmethod
    def _constant_long_seed_appender(cls, automate, l0, l1):
        x, y, z = 0, l0.popleft(), l0.popleft()
        cls.__append(automate, l1, x, y, z)
        for base in range(0, len(l0)):
            x, y, z = y, z, l0.popleft()
            cls.__append(automate, l1, x, y, z)
        cls.__append(automate, l1, y, z, 0)

    @classmethod
    def _descending_one_cell_appender(cls, automate, l0, l1):
        _ = l0.popleft()

    @classmethod
    def _descending_two_cells_appender(cls, automate, l0, l1):
        _, _ = l0.popleft(), l0.popleft()

    @classmethod
    def _descending_long_seed_appender(cls, automate, l0, l1):
        x, y, z = l0.popleft(), l0.popleft(), l0.popleft()
        cls.__append(automate, l1, x, y, z)
        for base in range(0, len(l0)):
            x, y, z = y, z, l0.popleft()
            cls.__append(automate, l1, x, y, z)

    @classmethod
    def __append(cls, automate, l, x, y, z):
        l.append(automate.next_step((x << 2) | (y << 1) | z))
