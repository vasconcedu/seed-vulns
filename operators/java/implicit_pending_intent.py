from operators.operators import Operator, OperatorTypes

class ImplicitPendingIntent(Operator):

    name = "ImplicitPendingIntent"
    type = OperatorTypes.JAVA

    def mutate(log, self):
        return super().mutate(self)
