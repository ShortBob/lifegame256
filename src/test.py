
from src.lines import plan_to_file, RunningPlanItem


def interesting_rules_gen():
    yield from (i for i in (225, 195, 193, 169, 149, 137, 121, 105, 101, 89, 30))

if __name__ == '__main__':
    plan_to_file(
        file_path_from_curdir='../../lgame.out',
        running_plan=(
            {'direction': '+', 'automate': 225, 'lines': 3},
            RunningPlanItem('+', 137, 3),
            ('-', 169, 5),
            {'direction': '-', 'automate': 169, 'lines': 60},
            {'direction': '+', 'automate': 137, 'lines': 60},
            {'direction': '-', 'automate': 30, 'lines': 60},
            {'direction': '+', 'automate': 121, 'lines': 60},
            {'direction': '=', 'automate': 105, 'lines': 60},
            {'direction': '=', 'automate': 101, 'lines': 60},
            {'direction': '-', 'automate': 195, 'lines': 60},
            {'direction': '+', 'automate': 89, 'lines': 60},
            {'direction': '-', 'automate': 147, 'lines': 25},
        ),
        seed=' XXX X   X   X X    X XX      XXXX X X X XXXXXXX XXX XX X X XX    XX     XXX  X  XXX    X X    X  X   XXX XX X    X  XXX',
        align=True,
    )
