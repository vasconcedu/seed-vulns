from random import randrange
import re
from operators.operators import Operator, OperatorNames, OperatorTypes

class TapjackingFullOcclusion(Operator):
    name = OperatorNames.TAPJACKING_FULL_OCCLUSION_JAVA
    type = OperatorTypes.JAVA

    # Different patterns for Java and Kotlin, though the operation is the same 
    # (change true to false)
    filterTouchesWhenObscuredJava = r"\.\s*?setFilterTouchesWhenObscured\s*?\(\s*?true\s*?\)"
    filterTouchesWhenObscuredKotlin = r"\.\s*?filterTouchesWhenObscured\s*?=\s*?true"

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, sourceHandler, commentMutations, allMutants):
        mutated = False 
        result = "\n========== Tapjacking Full Occlusion (Java) ==========\n"

        # Get sources
        sourceFiles = sourceHandler.findSourceFiles()
        self.log.info("Found %d sources:", len(sourceFiles))
        for sourceFile in sourceFiles:
            self.log.info("source: %s", sourceFile)

        # Find filter touches when obscured in source files
        candidateSourceFiles = sourceHandler.matchSourceFiles([self.filterTouchesWhenObscuredJava, self.filterTouchesWhenObscuredKotlin])
        self.log.info("Found %d candidate sources:", len(candidateSourceFiles))
        for sourceFile in candidateSourceFiles:
            self.log.info("Candidate source: %s", sourceFile["file"])

        if len(candidateSourceFiles) != 0:
            mutated = True 

            # Pick a pseudorandom candidate source file
            self.log.info("Picking a pseudorandom candidate source...")
            index = randrange(0, len(candidateSourceFiles))
            resultLine = "Picked source: " + candidateSourceFiles[index]["file"]
            resultLine += "\n- filterTouchesWhenObscured pattern: " + candidateSourceFiles[index]["pattern"]
            resultLine += "\n"
            result += resultLine
            self.log.info(resultLine)

            # Mutate source file
            # The operation is the same both for Java and Kotlin 
            # (change true to false)
            self.log.info("Mutating source...")
            self.log.info("Source is:")
            source = sourceHandler.readSourceFile(candidateSourceFiles[index]["file"])
            self.log.info(source)
            match = re.search(candidateSourceFiles[index]["pattern"], source)
            excerpt = source[match.start():match.end()]
            mutatedExcerpt = excerpt.replace("true", "false {}".format(self.getComment() if commentMutations else ""))
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
            self.log.info("Successfully wrote source to file")

        result += "========== End of Tapjacking Full Occlusion (Java) ==========\n"
        return result if mutated else None
    