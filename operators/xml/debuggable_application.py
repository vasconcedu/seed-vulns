from operators.operators import Operator, OperatorNames, OperatorTypes

class DebuggableApplication(Operator):

    name = OperatorNames.DEBUGGABLE_APPLICATION
    type = OperatorTypes.XML

    def mutate(self, destinationPath, manifestHandler):
        return {}
