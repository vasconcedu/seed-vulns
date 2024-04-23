from abc import abstractmethod
from enum import Enum

class OperatorTypes(Enum):
    XML = "XML"
    JAVA = "Java"

class OperatorNames(Enum):
    IMPROPER_EXPORT = "ImproperExport"
    DEBUGGABLE_APPLICATION = "DebuggableApplication"
    IMPLICIT_PENDING_INTENT = "ImplicitPendingIntent"

class Operator:
    @property
    def name(self):
        pass

    @property
    def type(self):
        pass

    def __init__(self, log):
        self.log = log

    @abstractmethod
    def mutate(self, destinationPath, handler=None):
        pass
