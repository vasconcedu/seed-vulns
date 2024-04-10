from operators.operators import Operator, OperatorNames, OperatorTypes

class ImplicitPendingIntent(Operator):

    name = OperatorNames.IMPLICIT_PENDING_INTENT
    type = OperatorTypes.JAVA

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, destinationPath):
        return ""
