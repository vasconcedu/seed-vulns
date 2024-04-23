import os
from random import randrange
import re
from operators.operators import Operator, OperatorNames, OperatorTypes

class ImplicitPendingIntent(Operator):

    name = OperatorNames.IMPLICIT_PENDING_INTENT
    type = OperatorTypes.JAVA

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

    def mutate(self, destinationPath, sourceHandler):
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
        
        # Pick a random candidate source file
        self.log.info("Picking a pseudorandom candidate source...")
        index = randrange(0, len(candidateSourceFiles))
        resultLine = "Picked source: " + candidateSourceFiles[index]["file"]
        resultLine += "\n- PI regex pattern: " + candidateSourceFiles[index]["pattern"]
        result += resultLine
        self.log.info(resultLine)

        # Mutate source file 
        self.log.info("Mutating source...")
        self.log.info("Source is:")
        source = sourceHandler.readSourceFile(candidateSourceFiles[index]["file"])
        self.log.info(source)
        match = re.search(candidateSourceFiles[index]["pattern"], source)
        excerpt = source[match.start():match.end()]
        mutatedExcerpt = excerpt.replace("FLAG_IMMUTABLE", "FLAG_MUTABLE")
        source = source.replace(excerpt, mutatedExcerpt)
        resultLine = "\nExcerpt:\n"
        resultLine += excerpt
        resultLine += "\nMutated excerpt:\n"
        resultLine += mutatedExcerpt
        resultLine += "\n"
        result += resultLine
        self.log.info(resultLine)
        
        self.log.info("Mutated source is:")
        self.log.info(source)

        # Write mutated source to file 
        self.log.info("Writing mutated source to file...")
        sourceHandler.writeSourceFile(candidateSourceFiles[index]["file"], source)

        result += "========== End of Implicit Pending Intent Operator ==========\n"
        return result
