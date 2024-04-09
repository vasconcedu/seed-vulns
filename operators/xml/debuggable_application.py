from operators.operators import Operator, OperatorNames, OperatorTypes

class DebuggableApplication(Operator):

    name = OperatorNames.DEBUGGABLE_APPLICATION
    type = OperatorTypes.XML

    def mutate(log, self):
        return super().mutate(self)
