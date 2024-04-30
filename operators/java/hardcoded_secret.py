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

    def mutate(self, sourceHandler):
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

            # Pick a pseudorandom candidate source file
            self.log.info("Picking a pseudorandom candidate source...")
            index = randrange(0, len(candidateSourceFiles))
            resultLine = "Picked source: " + candidateSourceFiles[index]["file"]
            resultLine += "\n"
            result += resultLine

            # Generate high entropy string 
            self.log.info("Generating secret...")
            secret = os.urandom(256).hex()
            self.log.info("Generated secret: %s", secret)

            self.log.info("Mutating source...")
            self.log.info("Source is:")
            source = sourceHandler.readSourceFile(candidateSourceFiles[index]["file"])
            self.log.info(source)

            # Inject hardcoded secret into beginning of class definition
            excerpt = None 
            mutatedExcerpt = None

            match = re.search(self.classDefinitionPattern, source)
            excerpt = source[match.start():match.end()]
            resultLine = "\nExcerpt:\n" + excerpt

            if sourceHandler.isJavaSourceFile(candidateSourceFiles[index]["file"]):
                mutatedExcerpt = excerpt + "\n\n    private static final String KEY = \"" + secret + "\";\n\n"
            elif sourceHandler.isKotlinSourceFile(candidateSourceFiles[index]["file"]):
                mutatedExcerpt = excerpt + "\n\n    private const val KEY = \"" + secret + "\"\n\n"
            source = source.replace(excerpt, mutatedExcerpt)

            resultLine += "\nMutated excerpt:\n" + mutatedExcerpt
            result += resultLine
            self.log.info(resultLine)

            self.log.info("Mutated source is:")
            self.log.info(source)

        result += "========== End of Hardcoded Secret Operator ==========\n"
        return result if mutated else None 
