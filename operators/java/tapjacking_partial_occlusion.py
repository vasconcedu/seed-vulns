from random import randrange
import re
from operators.operators import Operator, OperatorNames, OperatorTypes

class TapjackingPartialOcclusion(Operator):
    name = OperatorNames.TAPJACKING_PARTIAL_OCCLUSION
    type = OperatorTypes.JAVA

    # Different patterns for Java and Kotlin
    dispatchTouchEventPatternJava = r"public\s+?boolean\s+?dispatchTouchEvent\s*?\(\s*?MotionEvent(?s).*?\)\s*?{(?s).*?}"
    dispatchTouchEventPatternKotlin = r"override\s+?fun\s+?dispatchTouchEvent\s*?\((?s).*?:\s*?MotionEvent(?s).*?\)\s*?:\s*?Boolean\s*?{(?s).*?}"

    def __init__(self, log):
        super().__init__(log)

    def mutate(self, sourceHandler):
        mutated = False 
        result = "\n========== Tapjacking Partial Occlusion Operator ==========\n"

        # Get sources
        sourceFiles = sourceHandler.findSourceFiles()
        self.log.info("Found %d sources:", len(sourceFiles))
        for sourceFile in sourceFiles:
            self.log.info("Source: %s", sourceFile)

        # Find dispatch touch event methods in source files
        candidateSourceFiles = sourceHandler.matchSourceFiles([self.dispatchTouchEventPatternJava, self.dispatchTouchEventPatternKotlin])
        self.log.info("Found %d candidate sources:", len(candidateSourceFiles))
        for sourceFile in candidateSourceFiles:
            self.log.info("Candidate source: %s", sourceFile["file"])

        if len(candidateSourceFiles) != 0:
            mutated = True 

            # Pick a pseudorandom candidate source file
            self.log.info("Picking a pseudorandom candidate source...")
            index = randrange(0, len(candidateSourceFiles))
            resultLine = "Picked source: " + candidateSourceFiles[index]["file"]
            resultLine += "\n- dispatchTouchEvent regex pattern: " + candidateSourceFiles[index]["pattern"]
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
            mutatedExcerpt = "{{\n\n        return super.dispatchTouchEvent({}\n\n    }}"
            insert = None
            if sourceHandler.isJavaSourceFile(candidateSourceFiles[index]["file"]):
                insert = excerpt.split("(")[1].split("MotionEvent")[1].split(")")[0].strip()
                mutatedExcerpt = excerpt.replace(excerpt[excerpt.find("{"):], mutatedExcerpt.format(insert + ");"))
            elif sourceHandler.isKotlinSourceFile(candidateSourceFiles[index]["file"]):
                insert = excerpt.split("(")[1].split(":")[0].strip()
                mutatedExcerpt = excerpt.replace(excerpt[excerpt.find("{"):], mutatedExcerpt.format(insert + ")"))
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

        result += "========== End of Tapjacking Partial Occlusion Operator ==========\n"
        return result if mutated else None
    