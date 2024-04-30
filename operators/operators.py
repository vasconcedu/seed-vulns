from abc import abstractmethod
from enum import Enum

class OperatorTypes(Enum):
    XML_MANIFEST = "XML_MANIFEST"
    JAVA = "Java"
    XML_RESOURCES = "XML_RESOURCES"

class MutationComment(Enum):
    MUTATION_COMMENT_XML = " Mutated by seed-vulns " # No need for <!-- --> because lxml already includes it 
    MUTATION_COMMENT_JAVA = "/* Mutated by seed-vulns */"

class OperatorNames(Enum):
    IMPROPER_EXPORT = "ImproperExport"
    DEBUGGABLE_APPLICATION = "DebuggableApplication"
    IMPLICIT_PENDING_INTENT = "ImplicitPendingIntent"
    HARDCODED_SECRET = "HardcodedSecret"
    TAPJACKING_FULL_OCCLUSION = "TapjackingFullOcclusion" # Activates both Java and XML full occlusion operators
    TAPJACKING_FULL_OCCLUSION_JAVA = "TapjackingFullOcclusionJava"
    TAPJACKING_FULL_OCCLUSION_XML = "TapjackingFullOcclusionXml"
    TAPJACKING_PARTIAL_OCCLUSION = "TapjackingPartialOcclusion"
    TAPJACKING_SET_HIDE_OVERLAY_WINDOWS = "TapjackingSetHideOverlayWindows"
    PLAINTEXT_HTTP = "PlaintextHttp"

class Operator:

    @property
    def name(self):
        pass

    @property
    def type(self):
        pass

    def __init__(self, log):
        self.log = log

    def getComment(self):
        return MutationComment.MUTATION_COMMENT_XML.value if (
            self.type in [OperatorTypes.XML_MANIFEST, OperatorTypes.XML_RESOURCES]
        ) else MutationComment.MUTATION_COMMENT_JAVA.value 

    @abstractmethod
    def mutate(self, handler=None, commentMutations=False):
        pass
