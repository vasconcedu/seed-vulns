import os
from random import randrange
import re
from operators.operators import Operator, OperatorNames, OperatorTypes

class HardcodedSecret(Operator):
    name = OperatorNames.HARDCODED_SECRET
    type = OperatorTypes.JAVA

    # This pattern works interchangeably with Java and Kotlin, hence
    # there is no need to distinguish between the two file extensions.
    # Operand changes vary between languages, though. 
    classDefinitionPattern = r"class\s+[A-Za-z0-9_]+(?s).*?\{"

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, sourceHandler, commentMutations, allMutants):
        mutated = False 
        result = "\n========== Hardcoded Secret Operator ==========\n"

        # Get sources
        sourceFiles = sourceHandler.findSourceFiles()
        self.log.info("Found %d sources:", len(sourceFiles))
        for sourceFile in sourceFiles:
            self.log.info("Source: %s", sourceFile)

        # Find class definitions in source files
        candidateSourceFiles = sourceHandler.matchSourceFiles([self.classDefinitionPattern])
        self.log.info("Found %d candidate sources:", len(candidateSourceFiles))
        for sourceFile in candidateSourceFiles:
            self.log.info("Candidate source: %s", sourceFile["file"])

        if len(candidateSourceFiles) != 0:
            mutated = True 
            allMutantsIndex = 0

            # If not allMutants, then pick a pseudorandom candidate source
            # and only keep that one in the list
            if not allMutants:
                # Pick a pseudorandom candidate source file
                self.log.info("Picking a pseudorandom candidate source...")
                index = randrange(0, len(candidateSourceFiles))
                resultLine = "Picked source: " + candidateSourceFiles[index]["file"]
                resultLine += "\n"
                result += resultLine
                candidateSourceFiles = [candidateSourceFiles[index]]

            for candidateSourceFile in candidateSourceFiles:

                # Generate high entropy string 
                self.log.info("Generating secret...")
                secret = os.urandom(256).hex()
                self.log.info("Generated secret: %s", secret)

                self.log.info("Mutating source...")
                self.log.info("Source is:")
                source = sourceHandler.readSourceFile(candidateSourceFile["file"])
                self.log.info(source)

                # Inject hardcoded secret into beginning of class definition
                excerpt = None 
                mutatedExcerpt = None

                match = re.search(self.classDefinitionPattern, source)
                excerpt = source[match.start():match.end()]
                resultLine = "\nExcerpt:\n" + excerpt

                if sourceHandler.isJavaSourceFile(candidateSourceFile["file"]):
                    mutatedExcerpt = excerpt + "\n\n    private static final String KEY = \"" + secret + "\"; {}\n\n".format(self.getComment() if commentMutations else "")
                elif sourceHandler.isKotlinSourceFile(candidateSourceFile["file"]):
                    mutatedExcerpt = excerpt + "\n\n    private const val KEY = \"" + secret + "\" {}\n\n".format(self.getComment() if commentMutations else "")
                source = source.replace(excerpt, mutatedExcerpt)

                if allMutants:
                    resultLine += "\nMutant index is: {}".format(allMutantsIndex)

                resultLine += "\nMutated excerpt:\n" + mutatedExcerpt
                result += resultLine
                self.log.info(resultLine)

                self.log.info("Mutated source is:")
                self.log.info(source)

                # Write mutated source to file
                self.log.info("Writing mutated source to file...")
                if not allMutants:
                    sourceHandler.writeSourceFile(candidateSourceFile["file"], source)
                else: 
                    sourceHandler.writeSourceFile(candidateSourceFile["file"], source, True, "{}".format(allMutantsIndex))
                    allMutantsIndex += 1
                self.log.info("Successfully wrote source to file")

        # Remove base directory (no mutations there)
        if allMutants:
            sourceHandler.removeDestinationPath()

        result += "========== End of Hardcoded Secret Operator ==========\n"
        return result if mutated else None 
