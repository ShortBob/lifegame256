
from os import path, curdir
from src.lines import computed_plan


def interesting_rules_gen():
    yield from (i for i in (225, 195, 193, 169, 149, 137, 121, 105, 101, 89, 30))


def custom(running_plan, seed=(1,), call_back=print):
    lines = _gather_raw_lines(running_plan, seed)
    for line in _formatted_lines(lines):
        call_back(line)


def _gather_raw_lines(running_plan, seed):
    liner = computed_plan(running_plan, seed)
    lines = []
    for line in liner:
        lines.append(line)
    return lines


def _formatted_lines(lines):
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


def plan_to_file(file_path_from_curdir, running_plan, seed):
    file_path = path.join(path.abspath(curdir), file_path_from_curdir)
    with open(file_path, 'w') as output:

        def printer(line):
            output.write(line)
            output.write('\n')

        custom(
            running_plan=running_plan,
            seed=seed,
            call_back=printer,
        )


if __name__ == '__main__':
    plan_to_file(
        file_path_from_curdir='../../lgame.out',
        running_plan=(
            {'direction': '+', 'automate': 193, 'lines': 40},
            {'direction': '=', 'automate': 225, 'lines': 40},
            {'direction': '-', 'automate': 30, 'lines': 40},
        ),
        seed='X XX       XXXXXXXXXXX                    XXXXX         XXXXXXX  XXX  XXX           X',
    )
