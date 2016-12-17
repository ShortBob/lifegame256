
from os import path, curdir
from src.automate import AutomateCache
from src.lines import Liner


def _gather_raw_lines(running_plan, seed):
    liner = Liner(running_plan, seed)
    lines = []
    for line in liner.generator():
        lines.append(line)
    return lines


def _formatted_lines(lines):
    max_length = max(lines, key=lambda l: len(l))
    padding = int(max_length / 2)
    for padding, line in zip(padding, lines):
        yield ''.join(
            [
                ''.ljust(padding),
                ''.join(['X' if c == 1 else ' ' for c in line])
            ]
        )


def custom(running_plan, seed=(1,)):
    print('Seed={}\nExecuting : {}'.format(seed, running_plan))
    lines = _gather_raw_lines(running_plan, seed)
    print("Compute over.")
    for line in _formatted_lines(lines):
        print(line)


def every_256_on_n_lines(number_of_line_to_print, seed):
    custom(number_of_line_to_print, seed)


def rule_to_file(rule_number, number_of_line_to_print, file_path_string, pyramidal=False):
    file_path = path.join(path.abspath(curdir), file_path_string)
    with open(file_path, 'w') as file:
        automate_cache = AutomateCache()
        automate = automate_cache.get(rule_number)
        lines = _gather_raw_lines(automate, number_of_line_to_print)
        for printable in _formatted_lines(lines, number_of_line_to_print, pyramidal):
            file.write(printable)
            file.write('\n')


if __name__ == '__main__':
    custom(
        (
            {'direction': '+', 'automate': 101, 'lines': 20},
            {'direction': '=', 'automate': 101, 'lines': 20},
            {'direction': '-', 'automate': 101, 'lines': 20},
        ),
        # seed=' X XXXX  X    X  XX  XXX   X   XX   X  ',
        # seed='X XX       XXXXXXXXXXX                    XXXXX         XXXXXXX  XXX  XXX           X',
        seed='X',
    )
    # every_256_on_n_lines(30, seed='X XX       XXXXXXXXXXX                    XXXXX         XXXXXXX  XXX  XXX           X')
    # rule_to_file(101, 3000, 'automate101')
