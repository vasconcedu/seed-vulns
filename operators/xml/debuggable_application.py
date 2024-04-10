from operators.operators import Operator, OperatorNames, OperatorTypes

class DebuggableApplication(Operator):

    name = OperatorNames.DEBUGGABLE_APPLICATION
    type = OperatorTypes.XML

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, destinationPath, manifestHandler):
        return ""
