from random import randrange
import re
from operators.operators import Operator, OperatorNames, OperatorTypes

class TapjackingSetHideOverlayWindows(Operator):
    name = OperatorNames.TAPJACKING_SET_HIDE_OVERLAY_WINDOWS
    type = OperatorTypes.JAVA

    # Same pattern for Java and Kotlin
    setHideOverlayWindows = r"\.(?s)\s*?setHideOverlayWindows(?s)\s*?\((?s)\s*?true(?s)\s*?\)"

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, sourceHandler):
        mutated = False 
        result = "\n========== Tapjacking Set Hide Overlay Windows ==========\n"

        # Get sources
        sourceFiles = sourceHandler.findSourceFiles()
        self.log.info("Found %d sources:", len(sourceFiles))
        for sourceFile in sourceFiles:
            self.log.info("Source: %s", sourceFile)

        # Find set hide overlay windows calls in source files
        candidateSourceFiles = sourceHandler.matchSourceFiles([self.setHideOverlayWindows])
        self.log.info("Found %d candidate sources:", len(candidateSourceFiles))
        for sourceFile in candidateSourceFiles:
            self.log.info("Candidate source: %s", sourceFile["file"])

        if len(candidateSourceFiles) != 0:
            mutated = True 

            # Pick a pseudorandom candidate source file
            self.log.info("Picking a pseudorandom candidate source...")
            index = randrange(0, len(candidateSourceFiles))
            resultLine = "Picked source: " + candidateSourceFiles[index]["file"]
            resultLine += "\n- setHideOverlayWindows pattern: " + candidateSourceFiles[index]["pattern"]
            resultLine += "\n"
            result += resultLine
            self.log.info(resultLine)

            # Mutate source file
            self.log.info("Mutating source...")
            self.log.info("Source is:")
            source = sourceHandler.readSourceFile(candidateSourceFiles[index]["file"])
            self.log.info(source)
            match = re.search(candidateSourceFiles[index]["pattern"], source)
            excerpt = source[match.start():match.end()]
            mutatedExcerpt = excerpt.replace("true", "false")
            source = source.replace(excerpt, mutatedExcerpt)
            resultLine = "\nExcerpt:\n"
            resultLine += excerpt
            resultLine += "\nMutated excerpt:\n"
            resultLine += mutatedExcerpt
            result += resultLine + "\n"
            self.log.info(resultLine)

            self.log.info("Mutated source is:")
            self.log.info(source)

            # Write mutated source to file
            self.log.info("Writing mutated source to file...")
            sourceHandler.writeSourceFile(candidateSourceFiles[index]["file"], source)

        result += "========== End of Tapjacking Set Hide Overlay Windows ==========\n"
        return result if mutated else None
    