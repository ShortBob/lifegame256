
from collections import deque


def liner(automate_n):

    def __append_next_step(line_n1, x, y, z):
        line_n1.append(automate_n.next_step((x << 2) + (y << 1) + z))

    def generator():
        try:
            # First common line
            line_n0 = deque((1, ))
            yield tuple(line_n0)

            # Hard coded second line
            line_n1 = deque()
            line_n1.extend((
                automate_n.next_step((1 << 0)),
                automate_n.next_step((1 << 1)),
                automate_n.next_step((1 << 2)),
            ))
            line_n0, line_n1 = line_n1, deque()
            yield tuple(line_n0)

            # For every line having more than three computed cells
            while True:
                x, y, z = 0, 0, line_n0.popleft()
                __append_next_step(line_n1, x, y, z)
                for base in range(0, len(line_n0)):
                    x, y, z = y, z, line_n0.popleft()
                    __append_next_step(line_n1, x, y, z)
                x, y, z = y, z, 0
                __append_next_step(line_n1, x, y, z)
                x, y, z = y, z, 0
                __append_next_step(line_n1, x, y, z)
                line_n0, line_n1 = line_n1, deque()
                yield tuple(line_n0)
        except InterruptedError:
            pass

    generator.__name__ = '{}_generator'.format(automate_n.__class__.__name__)
    return generator
