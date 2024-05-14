from manifest.manifest_handler import ExportedConfig
from random import randrange
from operators.operators import Operator, OperatorNames, OperatorTypes

class ImproperExport(Operator):

    name = OperatorNames.IMPROPER_EXPORT
    type = OperatorTypes.XML_MANIFEST

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, manifestHandler, commentMutations, allMutants):
        mutated = False 
        result = "\n========== Improper Export Operator ==========\n"
        nonExportedComponents = None
        try:
            nonExportedComponents = manifestHandler.findAllApplicationComponents(exported=False)
            for component in nonExportedComponents:
                self.log.info("Component: %s is not exported. Reason: %s", component["name"], component["reason"])
        except Exception as e:
            self.log.error("An error occurred while finding all application components: %s. Exiting...", e)
            exit(1)

        if len(nonExportedComponents) != 0:
            mutated = True
            allMutantsIndex = 0

            if not allMutants:
                self.log.info("Pseudorandomly picking component to mutate...")
                index = randrange(0, len(nonExportedComponents))
                component = nonExportedComponents[index]
                resultLine = "Picked component: " + component["name"]
                self.log.info(resultLine)
                result += resultLine + "\n"
                nonExportedComponents = [component]

            for component in nonExportedComponents:
                self.log.info("Mutating component...")
                resultLine = "Component: " + component["name"]
                resultLine += "\n- tag: " + component["component"].tag
                resultLine += "\n- attrib: " + str(component["component"].attrib)
                if allMutants:
                    resultLine += "\nMutant index is: {}".format(allMutantsIndex)
                self.log.info(resultLine)
                result += resultLine + "\n"
                match component["reason"]:
                    case ExportedConfig.NOT_EXPORTED_EXPORTED_IS_FALSE:
                        component["component"].attrib["{" + list(manifestHandler.namespace.values())[0] + "}exported"] = "true"
                    case ExportedConfig.NOT_EXPORTED_INTENT_FILTER_NOT_PRESENT_AND_EXPORTED_NOT_PRESENT:
                        component["component"].attrib["{" + list(manifestHandler.namespace.values())[0] + "}exported"] = "true"
                    case _:
                        self.log.error("Invalid reason for non-exportation: %s", component["reason"])
                        exit(1)
                
                self.log.info("Successfully mutated component")
                resultLine = "Mutated component: " + component["name"]
                resultLine += "\n- tag: " + component["component"].tag
                resultLine += "\n- attrib: " + str(component["component"].attrib)
                self.log.info(resultLine)
                result += resultLine + "\n"
                
                self.log.info("Replacing component in manifest...")
                manifestHandler.replaceComponentAttrib(component["component"], component["name"], self.getComment())
                self.log.info("Successfully replaced component in manifest. New manifest is:")
                self.log.info(manifestHandler.getManifestString())

                self.log.info("Writing manifest to file...")
                if not allMutants:
                    manifestHandler.writeManifest()
                else:
                    manifestHandler.writeManifest(True, "{}".format(allMutantsIndex))
                    allMutantsIndex += 1
                self.log.info("Successfully wrote manifest to file")

        # Remove base directory (no mutations there)
        if allMutants and mutated:
            manifestHandler.removeDestinationPath()

        result += "========== End of Improper Export Operator ==========\n"
        return result if mutated else None
