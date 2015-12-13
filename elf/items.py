import abc

class ItemClass:
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, cardinality):
        self.name        = name
        self.cardinality = cardinality

    @abc.abstractmethod
    def lookup(self, id):
        """Translate an instance ID (zero-indexed, up to the
           stated cardinality) into a useful identifier."""
        return

class YesItem(ItemClass):
    def lookup(self, id):
        return str(self) + " ID: " + str(id)
