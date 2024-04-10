from manifest.manifest_handler import ExportedConfig
from random import randrange
from operators.operators import Operator, OperatorNames, OperatorTypes

class ImproperExport(Operator):

    name = OperatorNames.IMPROPER_EXPORT
    type = OperatorTypes.XML

    def __init__(self, log):
        super().__init__(log)

    def logNonExportedComponents(self, components):
        for component in components:
            self.log.info("Component: %s is not exported. Reason: %s", component["name"], component["reason"])

    def mutate(self, destinationPath, manifestHandler):
        nonExportedComponents = None
        try:
            nonExportedComponents = manifestHandler.findAllApplicationComponents(exported=False)
            self.logNonExportedComponents(nonExportedComponents)
        except Exception as e:
            self.log.error("An error occurred while finding all application components: %s. Exiting...", e)
            exit(1)

        self.log.info("Pseudorandomly picking component to mutate...")
        index = randrange(0, len(nonExportedComponents))
        component = nonExportedComponents[index]
        self.log.info("Picked component: %s", component["name"])
        self.log.info("- tag: %s", component["component"].tag)
        self.log.info("- attrib: %s", component["component"].attrib)

        self.log.info("Mutating component...")
        match component["reason"]:
            case ExportedConfig.NOT_EXPORTED_EXPORTED_IS_FALSE:
                component["component"].attrib["{" + list(manifestHandler.namespace.values())[0] + "}exported"] = "true"
            case ExportedConfig.NOT_EXPORTED_INTENT_FILTER_NOT_PRESENT_AND_EXPORTED_NOT_PRESENT:
                component["component"].attrib["{" + list(manifestHandler.namespace.values())[0] + "}exported"] = "true"
            case _:
                self.log.error("Invalid reason for non-exportation: %s", component["reason"])
                exit(1)
        
        self.log.info("Successfully mutated component: %s", component["name"])
        self.log.info("- tag: %s", component["component"].tag)
        self.log.info("- attrib: %s", component["component"].attrib)
        
        self.log.info("Replacing component in manifest...")
        manifestHandler.replaceComponentAttrib(component["component"], component["name"])
        self.log.info("Successfully replaced component in manifest. New manifest is:")
        self.log.info(manifestHandler.getManifestString())
