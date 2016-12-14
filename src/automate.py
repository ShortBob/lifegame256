__author__ = 'vincent farcette'


class AutomateMeta(type):

    # It is absolutely necessary to declare rule_number as a kwarg.
    def __new__(mcs, name, bases, namespace, *, rule_number=None):

        def next_step(self, initial_conditions):
            if not isinstance(initial_conditions, int) or not 0 <= initial_conditions < 8:
                raise ValueError('Initial conditions are represented by a int 0 <= initial_conditions < 8')
            return 1 if 1 << initial_conditions & self._rule_number else 0

        namespace = dict(namespace)
        namespace.update({'_rule_number': rule_number, 'next_step': next_step})
        return super().__new__(mcs, name, bases, dict(namespace))

    # It is absolutely necessary to declare rule_number as a kwarg.
    def __init__(cls, name, bases, namespace, *, rule_number=None):
        super().__init__(name, bases, namespace)


class AutomateCache(object):

    __CACHED_AUTOMATES = {}

    def get(self, rule_number):
        if rule_number not in self.__class__.__CACHED_AUTOMATES:
            self.__class__.__CACHED_AUTOMATES[rule_number] = self.__class__._create_automate_class(rule_number)
        automate_class = self.__class__.__CACHED_AUTOMATES[rule_number]
        return automate_class()

    @classmethod
    def _create_automate_class(cls, rule_number):
        if not isinstance(rule_number, int):
            raise TypeError('Only numbers can be considered as valid rule_number.')
        if not 0 <= rule_number <= 255 :
            raise ValueError('Only rules 0 <= rule_number <= 255 makes sense.')
        name = 'Automate{}'.format(rule_number)
        bases = (object,)
        namespace = {'metaclass': AutomateMeta}
        return AutomateMeta(name, bases, namespace, rule_number=rule_number)
