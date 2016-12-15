
__author__ = 'Vincent Farcette'


class AutomateMeta(type):
    """
    Metaclass used to create a linear cellular automate class able to compute the next state of a cell.
    When used, rule_number must be defined as a keyword argument.
    ex :

    class Automate30(object, metaclass=AutomateMeta, rule_number=30):
        pass

    or

    Automate30 = AutomateMeta('Automate30', (object,) , {'metaclass": AutomateMeta, ...}, rule_number=rule_number)
    """

    # It is absolutely necessary to declare rule_number as a kwarg.
    def __new__(mcs, name, bases, namespace, *, rule_number=None):

        def next_step(self, initial_conditions):
            """
            Compute the state of the future cell.
            :param self:
            :param initial_conditions: three bytes int representing state of three cells predecessor.
            :return: 1 or 0 depending on initial_conditions and self._rule_number.
            """
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

    """
    Class using AutomateMeta to create and cache concrete AutomateN classes.
    Usage :
    cache = AutomateCache()
    rule_number = 12
    automate12_instance = cache.get(rule_number)    # If this is the first call of cache.get(12), class is cached.
                                                    # Anyway, an instance of Automate12 is returned.

    AutomateN instance has an next_step(initial_conditions) method.
    """

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
