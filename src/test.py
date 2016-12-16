
from src.automate import AutomateCache
from src.lines import liner

LINES = 30

if __name__ == '__main__':
    automate_cache = AutomateCache()
    automate_30 = automate_cache.get(30)
    gen = liner(automate_30)
    lines = []
    for i, line in enumerate(gen()):
        lines.append(tuple(line))
        if i > LINES:
            break

    for i, line in enumerate(lines):
        print(''.ljust((int((LINES * 2 + 1) / 2)) - (i % 1) - int(i / 2)), end='')
        print(''.join([str(c) for c in line]))

