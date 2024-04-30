from operators.operators import Operator, OperatorNames, OperatorTypes

class PlaintextHttp(Operator):

    name = OperatorNames.PLAINTEXT_HTTP
    type = OperatorTypes.XML_MANIFEST

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, manifestHandler, commentMutations):
        mutated = False 
        result = "\n========== Plaintext HTTP Operator ==========\n"

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

        match application.attrib.get("{" + list(manifestHandler.namespace.values())[0] + "}usesCleartextTraffic"):
            case "true":
                self.log.info("Application already uses cleartext traffic. Skipping...")
                return None 
            case "false" | None :
                mutated = True
                application.attrib["{" + list(manifestHandler.namespace.values())[0] + "}usesCleartextTraffic"] = "true"
                self.log.info("Application does not use cleartext traffic. Mutating...")
                manifestHandler.replaceApplicationAttrib(application, self.getComment())
                self.log.info("Successfully mutated application. New manifest is:")
                self.log.info(manifestHandler.getManifestString())
            case _:
                self.log.error("Invalid value for usesCleartextTraffic: %s", application.attrib.get("{" + list(manifestHandler.namespace.values())[0] + "}usesCleartextTraffic"))
                exit(1)
        
        resultLine = "Mutated application:"
        resultLine += "\n- attrib: " + application.attrib.__str__()
        self.log.info(resultLine)
        result += resultLine + "\n"

        self.log.info("Writing manifest to file...")
        manifestHandler.writeManifest()
        self.log.info("Successfully wrote manifest to file")

        result += "========== End of Plaintext HTTP Operator ==========\n"
        return result if mutated else None
