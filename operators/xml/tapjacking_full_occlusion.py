from random import randrange
import re
from operators.operators import Operator, OperatorNames, OperatorTypes

class TapjackingFullOcclusion(Operator):
    name = OperatorNames.TAPJACKING_FULL_OCCLUSION_XML
    type = OperatorTypes.XML_RESOURCES

    filterTouchesWhenObscured = r"filterTouchesWhenObscured=\"true\""

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, resourcesHandler, commentMutations, allMutants):
        mutated = False 
        result = "\n========== Tapjacking Full Occlusion (XML) ==========\n"

        # Get resources
        resourceFiles = resourcesHandler.findResourceFiles()
        self.log.info("Found %d resources:", len(resourceFiles))
        for resourceFile in resourceFiles:
            self.log.info("Resource: %s", resourceFile)

        # Find filter touches when obscured in resource files
        candidateResourceFiles = resourcesHandler.matchResourceFiles([self.filterTouchesWhenObscured])
        self.log.info("Found %d candidate resources:", len(candidateResourceFiles))
        for resourceFile in candidateResourceFiles:
            self.log.info("Candidate resource: %s", resourceFile["file"])

        if len(candidateResourceFiles) != 0:
            mutated = True 
            allMutantsIndex = 0

            if not allMutants:
                # Pick a pseudorandom candidate resource file
                self.log.info("Picking a pseudorandom candidate resource...")
                index = randrange(0, len(candidateResourceFiles))
                resultLine = "Picked resource: " + candidateResourceFiles[index]["file"]
                resultLine += "\n- filterTouchesWhenObscured pattern: " + candidateResourceFiles[index]["pattern"]
                resultLine += "\n"
                result += resultLine
                self.log.info(resultLine)
                candidateResourceFiles = [candidateResourceFiles[index]]

            for candidate in candidateResourceFiles:
                # Mutate source file
                self.log.info("Mutating resource...")
                self.log.info("Resource is:")
                resource = resourcesHandler.readResourceFile(candidate["file"])
                self.log.info(resource)
                match = re.search(candidate["pattern"], resource)
                excerpt = resource[match.start():match.end()]
                mutatedExcerpt = excerpt.replace("true", "false")
                resource = resource.replace(excerpt, mutatedExcerpt)

                # TODO improve, this is due to the current resources handler parsing limitation
                resource = resource.replace("</application>", "<!--{}--></application>".format(self.getComment()))

                resultLine = "\nExcerpt:\n"
                resultLine += excerpt
                if allMutants:
                    resultLine += "\nMutant index is: {}".format(allMutantsIndex)
                resultLine += "\nMutated excerpt:\n"
                resultLine += mutatedExcerpt
                result += resultLine + "\n"
                self.log.info(resultLine)

                self.log.info("Mutated resource is:")
                self.log.info(resource)

                # Write mutated resource to file
                self.log.info("Writing mutated resource to file...")
                if not allMutants:
                    resourcesHandler.writeResourceFile(candidate["file"], resource)
                else: 
                    resourcesHandler.writeResourceFile(candidate["file"], resource, True, "{}".format(allMutantsIndex))
                    allMutantsIndex += 1
                self.log.info("Successfully wrote resource to file")

        if allMutants and mutated:
            resourcesHandler.removeDestinationPath()

        result += "========== End of Tapjacking Full Occlusion (XML) ==========\n"
        return result if mutated else None
    