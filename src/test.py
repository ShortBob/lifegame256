
from os import path, curdir
from src.automate import AutomateCache
from src.lines import computed_plan


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
                ''.ljust(max_padding - int(len(line)/2), '%'),
                ''.join(['X' if c == 1 else ' ' for c in line]),
                ''.ljust(max_padding - int(len(line)/2), '%'),
            ]
        )


def custom(running_plan, seed=(1,), call_back=print):
    lines = _gather_raw_lines(running_plan, seed)
    for line in _formatted_lines(lines):
        call_back(line)


def every_256_on_n_lines(number_of_line_to_print, seed):
    running_plan = []
    for i in range(0, 256):
        running_plan.append({'direction': '+', 'automate': i, 'lines': number_of_line_to_print})
    custom(running_plan, seed)


def interesting_rules_gen():
    yield from (i for i in (225, 195, 193, 169, 149, 137, 121, 105, 101, 89, 30))


def rule_to_file(rule_number, number_of_line_to_print, file_path_string):
    file_path = path.join(path.abspath(curdir), file_path_string)
    with open(file_path, 'w') as file:
        lines = _gather_raw_lines(({'direction': '+', 'automate': rule_number, 'lines': number_of_line_to_print},), seed=(1,))
        for printable in _formatted_lines(lines):
            file.write(printable)
            file.write('\n')


if __name__ == '__main__':
    with open('/home/vincent/python_sandbox/lgame.out', 'w') as output:
        def printer(line):
            output.write(line)
            output.write('\n')
        custom(
            running_plan=(
                {'direction': '+', 'automate': 101, 'lines': 40},
                {'direction': '=', 'automate': 225, 'lines': 40},
                {'direction': '-', 'automate': 30, 'lines': 40},
            ),
            seed='X XX       XXXXXXXXXXX                    XXXXX         XXXXXXX  XXX  XXX           X',
            call_back=printer,
        )
