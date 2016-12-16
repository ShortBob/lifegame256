
from os import path, curdir
from src.automate import AutomateCache
from src.lines import liner


def _gather_raw_lines(automate_n, number_of_line_to_print):
    gen = liner(automate_n)
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


def every_256_on_n_lines(number_of_line_to_print):
    automate_cache = AutomateCache()
    for rule_number in range(0, 256):
        automate_n = automate_cache.get(rule_number)
        print('{:*^25}'.format(automate_n.__class__.__name__))
        lines = _gather_raw_lines(automate_n, number_of_line_to_print)
        for printable in _formatted_lines(lines, number_of_line_to_print):
            print(printable)


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
    # every_256_on_n_lines(30)
    rule_to_file(101, 3000, 'automate101')
