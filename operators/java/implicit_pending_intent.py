import os
from random import randrange
import re
from operators.operators import Operator, OperatorNames, OperatorTypes

class ImplicitPendingIntent(Operator):

    name = OperatorNames.IMPLICIT_PENDING_INTENT
    type = OperatorTypes.JAVA

    # This pattern works interchangeably with Java and Kotlin, hence
    # there is no need to distinguish between the two file extensions
    explicitPendingIntentPatterns = [ 
        r"PendingIntent(\s+)?\.(\s+)?get{}(\s+)?\((?s).*?PendingIntent(\s+)?\.(\s+)?FLAG_IMMUTABLE(?s).*?\)"
            .format(pattern) 
        for pattern in [
            "Activities",
            "Activity",
            "Broadcast",
            "Service",
            "ForegroundService"
        ]
    ]

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, sourceHandler, commentMutations, allMutants):
        mutated = False  
        result = "\n========== Implicit Pending Intent Operator ==========\n"

        # Get sources
        sourceFiles = sourceHandler.findSourceFiles()
        self.log.info("Found %d sources:", len(sourceFiles))
        for sourceFile in sourceFiles:
            self.log.info("Source: %s", sourceFile)

        # Look for explicit pending intents in source files
        candidateSourceFiles = sourceHandler.matchSourceFiles(self.explicitPendingIntentPatterns) 
        self.log.info("Found %d candidate sources:", len(candidateSourceFiles))
        for sourceFile in candidateSourceFiles:
            self.log.info("Candidate source: %s. Pattern: %s", sourceFile["file"], sourceFile["pattern"])

        if len(candidateSourceFiles) != 0:
            mutated = True 
            allMutantsIndex = 0
        
            if not allMutants: 
                # Pick a random candidate source file
                self.log.info("Picking a pseudorandom candidate source...")
                index = randrange(0, len(candidateSourceFiles))
                resultLine = "Picked source: " + candidateSourceFiles[index]["file"]
                resultLine += "\n- PI regex pattern: " + candidateSourceFiles[index]["pattern"]
                result += resultLine
                self.log.info(resultLine)
                candidateSourceFiles = [candidateSourceFiles[index]]

            for candidate in candidateSourceFiles:
                # Mutate source file 
                self.log.info("Mutating source...")
                self.log.info("Source is:")
                source = sourceHandler.readSourceFile(candidate["file"])
                self.log.info(source)
                match = re.search(candidate["pattern"], source)
                excerpt = source[match.start():match.end()]
                mutatedExcerpt = excerpt.replace("FLAG_IMMUTABLE", "FLAG_MUTABLE {}".format(self.getComment() if commentMutations else ""))
                source = source.replace(excerpt, mutatedExcerpt)
                resultLine = "\nExcerpt:\n"
                resultLine += excerpt
                if allMutants:
                    resultLine += "\nMutant index is: {}".format(allMutantsIndex)
                resultLine += "\nMutated excerpt:\n"
                resultLine += mutatedExcerpt
                resultLine += "\n"
                result += resultLine
                self.log.info(resultLine)
                
                self.log.info("Mutated source is:")
                self.log.info(source)

                # Write mutated source to file 
                self.log.info("Writing mutated source to file...")
                if not allMutants:
                    sourceHandler.writeSourceFile(candidate["file"], source)
                else: 
                    sourceHandler.writeSourceFile(candidate["file"], source, True, "{}".format(allMutantsIndex))
                    allMutantsIndex += 1
                self.log.info("Successfully wrote source to file")

        # Remove base directory (no mutations there)
        if allMutants and mutated:
            sourceHandler.removeDestinationPath()

        result += "========== End of Implicit Pending Intent Operator ==========\n"
        return result if mutated else None
