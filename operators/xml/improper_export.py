from operators.operators import Operator, OperatorNames, OperatorTypes

class ImproperExport(Operator):

    name = OperatorNames.IMPROPER_EXPORT
    type = OperatorTypes.XML

    def mutate(self, destinationPath, manifestHandler):
        return {}
