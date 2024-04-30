from abc import abstractmethod
from enum import Enum

class OperatorTypes(Enum):
    XML = "XML"
    JAVA = "Java"

class OperatorNames(Enum):
    IMPROPER_EXPORT = "ImproperExport"
    DEBUGGABLE_APPLICATION = "DebuggableApplication"
    IMPLICIT_PENDING_INTENT = "ImplicitPendingIntent"
    HARDCODED_SECRET = "HardcodedSecret"
    TAPJACKING_PARTIAL_OCCLUSION = "TapjackingPartialOcclusion"
    TAPJACKING_SET_HIDE_OVERLAY_WINDOWS = "TapjackingSetHideOverlayWindows"

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
    def mutate(self, handler=None):
        pass
