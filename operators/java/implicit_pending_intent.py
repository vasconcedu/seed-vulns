from operators.operators import Operator, OperatorNames, OperatorTypes

class ImplicitPendingIntent(Operator):

    name = OperatorNames.IMPLICIT_PENDING_INTENT
    type = OperatorTypes.JAVA

    def mutate(self, destinationPath):
        return {}
