
from src.automate import AutomateCache
from src.lines import liner

LINES = 30

if __name__ == '__main__':
    automate_cache = AutomateCache()
    for rule_number in range(0, 256):
        automate_n = automate_cache.get(rule_number)
        print('{:*^25}'.format(automate_n.__class__.__name__))
        gen = liner(automate_n)
        lines = []
        for i, line in enumerate(gen()):
            lines.append(line)
            if i > LINES:
                break

        for i, line in enumerate(lines):
            print(''.ljust(LINES - i + 1), end='')
            print(''.join(['X' if c == 1 else ' ' for c in line]))

