from operators.operators import Operator, OperatorTypes

class ImproperExport(Operator):

    name = "ImproperExport"
    type = OperatorTypes.XML

    def mutate(log, self):
        return super().mutate(self)
