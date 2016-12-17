
from os import path, curdir
from src.automate import AutomateCache
from src.lines import liner


def _gather_raw_lines(automate_n, number_of_line_to_print, seed):
    gen = liner(automate_n, seed)
    lines = []
    for i, line in enumerate(gen()):
        lines.append(line)
        if i > number_of_line_to_print:
            break
    return lines


def _formatted_lines(lines, number_of_line_to_print, pyramidal=True):
    for i, line in enumerate(lines):
        yield ''.join(
            [
                ''.ljust(number_of_line_to_print - i + 1 if pyramidal else 0),
                ''.join(['X' if c == 1 else ' ' for c in line])
            ]
        )


def custom(numb_line_to_print=0, seed=(1,), rules=(i for i in range(0, 256))):
    automate_cache = AutomateCache()
    for rule_number in rules:
        automate_n = automate_cache.get(rule_number)
        print('{:*^25}'.format(automate_n.__class__.__name__))
        lines = _gather_raw_lines(automate_n, numb_line_to_print, seed)
        for printable in _formatted_lines(lines, numb_line_to_print):
            print(printable)


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
        60,
        # seed=' X XXXX  X    X  XX  XXX   X   XX   X  ',
        # seed='X XX       XXXXXXXXXXX                    XXXXX         XXXXXXX  XXX  XXX           X',
        seed='X',
        rules=(225, 195, 193, 169, 149, 137, 121, 105, 101, 89, 30),
    )
    # every_256_on_n_lines(30, seed='X XX       XXXXXXXXXXX                    XXXXX         XXXXXXX  XXX  XXX           X')
    # rule_to_file(101, 3000, 'automate101')
