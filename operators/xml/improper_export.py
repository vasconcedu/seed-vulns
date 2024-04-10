from operators.operators import Operator, OperatorNames, OperatorTypes

class ImproperExport(Operator):

    name = OperatorNames.IMPROPER_EXPORT
    type = OperatorTypes.XML

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, destinationPath, manifestHandler):
        try:
            applicationComponents = manifestHandler.findAllApplicationComponents(True)
        except Exception as e:
            self.log.error("An error occurred while finding all application components: %s. Exiting...", e)
            exit(1)
        return {}
