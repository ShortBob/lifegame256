
from os import path, curdir
from collections import Iterable, Sized, deque, namedtuple
from src.automate import AutomateCache


RunningPlanItem = namedtuple('RunningPlan', ('direction', 'automate', 'lines'))
RunningPlanItem.__doc__ = """
namedtuple class representing a unitary value of a running plan.
Each unit contains 'direction', 'automate' and 'lines'.
Valid values are :
        * direction : '+', '=' or '-'
        * automate : 0 <= n <= 255
        * lines : 0 < n
"""

running_plan_item_definition = RunningPlanItem(
    lambda d: d in ('+', '=', '-'),
    lambda a: isinstance(a, int) and 0 <= a <= 255,
    lambda l: isinstance(l, int) and l >= 0,
)


def validate_and_return_seed(seed):
    """
    Check if seed is valid (raises if not) and returns a valid (eventually converted) copy of it.
    :param seed: Seed from which computation occurs. Have to be (0, 1, .., 1) like, or 'X X  ... X ' like.
    :return: computed valid copy of seed.
    """
    if not isinstance(seed, (tuple, list, deque, str)):
        raise ValueError('seed have to be tuple, list, deque, or str')
    if not all(isinstance(s, int) or s in (' ', 'X') for s in seed):
        raise ValueError('seed must be int or "X  X XXX X" (i.e. r"([X ]+)"). Found : {}'.format(seed))
    if len(seed) < 0:
        raise ValueError('seed can not be empty')
    if isinstance(seed, str):
        (*seed2,) = (1 if s == 'X' else 0 for s in seed)
        return seed2
    return tuple(seed)


def validate_and_return_running_plan(running_plan):
    """
    Check if the given running_plan is valid and returns a copy of it.

    Valid running plans are iterable. Every items inside it is supposed to be either a RunningPlanItem, a dict with
    exactly 'direction', 'automate' and 'lines' has keys, or an raw three valued iterable with items compliant to
    definition.

    Example :
    (
        RunningPlanItem('+', 125, 12),
        {'direction': '-', 'automate': 112, 'lines': 37},
        ( ('=', 132, 23), ['-', 119, 11], )
    )
    Valid values are :
        * direction : '+', '=' or '-'
        * automate : 0 <= n <= 255
        * lines : 0 < n

    Pre-validation can be made using running_plan_item_definition which is RunningPlantItem
    containing lambda instead of values which return True if the given value complies.
    :param running_plan: Given running plan to check before copy and return
    :return: New validated running plan, as tuple of RunningPlanItems.
    """
    validated = []
    test_direction = running_plan_item_definition.direction
    test_automate = running_plan_item_definition.automate
    test_lines = running_plan_item_definition.lines

    if not isinstance(running_plan, Iterable) and not isinstance(running_plan, (str, bytes)):
        raise ValueError('running_plan have to be an Iterable')

    for inner_plan in running_plan:
        if isinstance(inner_plan, dict):
            if not 0 == len(set(running_plan_item_definition._fields) ^ set(inner_plan.keys())):
                raise KeyError('authorised and mandatory keys in running_plan item have to be {}'.format(
                    running_plan_item_definition._fields)
                )
            for key, value in inner_plan.items():
                test_lambda = getattr(running_plan_item_definition, key, None)
                if not test_lambda(value):
                    raise ValueError('value: {} of key: {} in running_plan item {} is not check compliant. Code is {}'.format(
                        value, key, inner_plan, getattr(running_plan_item_definition, key, None).__code__
                    ))
            validated.append(RunningPlanItem(**inner_plan))

        elif isinstance(inner_plan, (Iterable, Sized)) and not isinstance(running_plan, (str, bytes)):
            if len(inner_plan) != 3:
                raise ValueError('running_plan iterable must be composed of three valued items like (X, Y, Z).')
            direction, automate, lines = inner_plan
            if not test_direction(direction) or not test_automate(automate) or not test_lines(lines):
                raise ValueError('Invalid running_plan. Error lies in triplet ({}, {}, {})'.format(
                    direction, automate, lines
                ))
            validated.append(RunningPlanItem(direction, automate, lines))

        else:
            raise ValueError('Every item in running_plan have to be dict or Iterable made of three items iterable.'
                             ' Definition can be validated with lambda of running_plan_item_definition.')

    return validated


class LinerMeta(type):
    """
    Metaclass to use to create custom designed class made that its instance is an iterable returning computed lines
    from a given seed and a given running plan.
    """

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
    def __ascending(mcs, self, automate, lines_count):
        if len(self._l0) == 1:
            yield from mcs._step_with_appender(mcs._ascending_one_cell_appender, automate, self._l0, self._l1)
            self._l0, self._l1 = self._l1, self._l0
            lines_count -= 1

        if len(self._l0) == 2:
            yield from mcs._step_with_appender(mcs._ascending_two_cells_appender, automate, self._l0, self._l1)
            self._l0, self._l1 = self._l1, self._l0
            lines_count -= 1

        while lines_count > 0:
            yield from mcs._step_with_appender(mcs._ascending_long_seed_appender, automate, self._l0, self._l1)
            self._l0, self._l1 = self._l1, self._l0
            lines_count -= 1

    @classmethod
    def __steadying(mcs, self, automate, lines_count):
        if len(self._l0) == 1:
            yield from mcs._step_with_appender(mcs._constant_one_cell_appender, automate, self._l0, self._l1)
            self._l0, self._l1 = self._l1, self._l0
            lines_count -= 1

        if len(self._l0) == 2:
            yield from mcs._step_with_appender(mcs._constant_two_cells_appender, automate, self._l0, self._l1)
            self._l0, self._l1 = self._l1, self._l0
            lines_count -= 1

        while lines_count > 0:
            yield from mcs._step_with_appender(mcs._constant_long_seed_appender, automate, self._l0, self._l1)
            self._l0, self._l1 = self._l1, self._l0
            lines_count -= 1

    @classmethod
    def __descending(mcs, self, automate, lines_count):
        if len(self._l0) == 1:
            yield from mcs._step_with_appender(mcs._descending_one_cell_appender, automate, self._l0, self._l1)
            self._l0, self._l1 = self._l1, self._l0
            lines_count -= 1

        if len(self._l0) == 2:
            yield from mcs._step_with_appender(mcs._descending_two_cells_appender, automate, self._l0, self._l1)
            self._l0, self._l1 = self._l1, self._l0
            lines_count -= 1

        while lines_count > 0:
            yield from mcs._step_with_appender(mcs._descending_long_seed_appender, automate, self._l0, self._l1)
            self._l0, self._l1 = self._l1, self._l0
            lines_count -= 1

    def __new__(mcs, name, bases, namespace, *_, running_plan=None, seed=(1,), **kwargs):
        """
        Creates a new class designed to run given plan from given seed.
        :param name: New class name
        :param bases: New class bases (intended to be (object, ))
        :param namespace: New class namespace
        :param _: throw out args for signature coherence
        :param running_plan: The given running plan to run
        :param seed: The given seed to run from
        :param kwargs: throw out kwargs for signature coherence
        :return: Custom class
        """
        rp = validate_and_return_running_plan(running_plan)
        checked_seed = validate_and_return_seed(seed)
        cache = AutomateCache()

        namespace = dict(namespace)
        namespace.update(
            {
                '_seed': checked_seed,
                '_running_plan': rp,
                '_cache': cache,
            }
        )

        _executable_plans = []
        for one_plan in rp:
            direction = one_plan.direction
            automate_instance = cache.get(one_plan.automate)
            lines = one_plan.lines
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
                    yield from nx_func(self, nx_automate, nx_lines)
            except StopIteration:
                pass

        namespace.update({'__iter__': __iter__})

        return super().__new__(mcs, name, bases, dict(namespace))

    def __init__(cls, name, bases, namespace, *_, running_plan=None, seed=(1,), **kwargs):
        super().__init__(name, bases, dict(namespace))


def computed_plan(running_plan, seed):
    """
    Returns an instance of AutomatePlanExecutor, designed to execute the given running plan, from the given seed.
    """
    name = 'AutomatePlanExecutor'
    bases = (object,)
    namespace = {'metaclass': LinerMeta}
    custom_class_runner = LinerMeta(name, bases, namespace, running_plan=running_plan, seed=seed)
    return custom_class_runner()


def custom(running_plan, seed=(1,), call_back=print, align=True):
    """
    Execute running_plan starting from seed, using call_back to handle every line result, eventually aligned.
    :param running_plan: Plan to run
    :param seed: Seed from which start computing
    :param call_back: Called for every result line
    :param align: Tell whether or not lines have to be formatted (i.e. padded)
    """
    lines = _gather_raw_lines(running_plan, seed)
    final_lines = _align_lines(lines) if align else lines
    for line in final_lines:
        call_back(line)


def _gather_raw_lines(running_plan, seed):
    liner = computed_plan(running_plan, seed)
    lines = []
    for line in liner:
        lines.append(line)
    return lines


def _align_lines(lines):
    max_length = len(max(lines, key=lambda l: len(l)))
    max_padding = int(max_length / 2)
    for line in lines:
        yield ''.join(
            [
                ''.ljust(max_padding + 1 - int(len(line)/2), '|'),
                ''.join(['X' if c == 1 else ' ' for c in line]),
                ''.ljust(max_padding + 1 - int(len(line)/2), '|'),
            ]
        )


def plan_to_file(file_path_from_curdir, running_plan, seed, align):
    """
    Use it to simply write execution result to a given file.
    It uses custom with an already given call_back function that print every line into the given file.
    :param file_path_from_curdir: Path of the destination file seen from os.curdir
    :param running_plan: Running plan to execute
    :param seed: Seed from which execute the running_plan
    :param align: If True, result lines are aligned (left and right padding)
    """
    file_path = path.join(path.abspath(curdir), file_path_from_curdir)
    with open(file_path, 'w') as output:

        def printer(line):
            output.write(line)
            output.write('\n')

        custom(
            running_plan=running_plan,
            seed=seed,
            call_back=printer,
            align=align,
        )
