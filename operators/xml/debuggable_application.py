from operators.operators import Operator, OperatorNames, OperatorTypes

class DebuggableApplication(Operator):

    name = OperatorNames.DEBUGGABLE_APPLICATION
    type = OperatorTypes.XML_MANIFEST

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, manifestHandler):
        result = "\n========== Debuggable Application Operator ==========\n"

        application = None
        try:
            self.log.info("Finding application...")
            application = manifestHandler.findApplication()
        except Exception as e:
            self.log.error("An error occurred while finding applications: %s. Exiting...", e)
            exit(1)

        if len(application) != 1:
            self.log.error("Inconsistent manifest: must contain one and only one application. Exiting...", len(application))
            exit(1)

        application = application[0]
        resultLine = "Application:"
        resultLine += "\n- attrib: " + application.attrib.__str__()
        self.log.info(resultLine)
        result += resultLine + "\n"

        match application.attrib.get("{" + list(manifestHandler.namespace.values())[0] + "}debuggable"):
            case "true":
                self.log.info("Application is already debuggable. Skipping...")
                return ""
            case "false":
                application.attrib["{" + list(manifestHandler.namespace.values())[0] + "}debuggable"] = "true"
                self.log.info("Application is not debuggable. Mutating...")
                manifestHandler.replaceApplicationAttrib(application)
                self.log.info("Successfully mutated application. New manifest is:")
                self.log.info(manifestHandler.getManifestString())
            case _:
                self.log.error("Invalid value for debuggable: %s", application.attrib.get("{" + list(manifestHandler.namespace.values())[0] + "}debuggable"))
                exit(1)
        
        resultLine = "Mutated application:"
        resultLine += "\n- attrib: " + application.attrib.__str__()
        self.log.info(resultLine)
        result += resultLine + "\n"

        self.log.info("Writing manifest to file...")
        manifestHandler.writeManifest()
        self.log.info("Successfully wrote manifest to file")

        result += "========== End of Debuggable Application Operator ==========\n"
        return result 
