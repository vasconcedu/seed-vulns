from abc import abstractmethod
from enum import Enum

class OperatorTypes(Enum):
    XML = "XML"
    JAVA = "Java"

class Operator:
    @property
    def name(self):
        pass

    @property
    def type(self):
        pass

    @abstractmethod
    def mutate(log, self):
        pass
