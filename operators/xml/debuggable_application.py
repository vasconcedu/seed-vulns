from operators.operators import Operator, OperatorTypes

class DebuggableApplication(Operator):

    name = "DebuggableApplication"
    type = OperatorTypes.XML

    def mutate(log, self):
        return super().mutate(self)
