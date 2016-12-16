
from collections import deque


def liner(automate_n):

    def generator():
        i = 0
        try:
            line_n0 = deque((1, ))
            yield line_n0
            line_n0 = deque([1, ])
            line_n1 = deque()
            line_n1.extend((
                automate_n.next_step((1)),
                automate_n.next_step((1 << 1)),
                automate_n.next_step((1 << 2)),
            ))
            line_n0, line_n1 = line_n1, deque()
            yield line_n0
            while True:
                x, y, z = 0, line_n0.popleft(), line_n0.popleft()
                line_n1.append(automate_n.next_step((x << 2) + (y << 1) + z))
                for base in range(0, len(line_n0)):
                    x, y, z = y, z, line_n0.popleft()
                    line_n1.append(automate_n.next_step((x << 2) + (y << 1) + z))
                x, y, z = y, z, 0
                line_n1.append(automate_n.next_step((x << 2) + (y << 1) + z))
                x, y, z = y, z, 0
                line_n1.append(automate_n.next_step((x << 2) + (y << 1) + z))
                line_n0, line_n1 = line_n1, deque()
                yield line_n0
                i += 1
        except InterruptedError:
            pass

    generator.__name__ = '{}_generator'.format(automate_n.__class__.__name__)
    return generator
