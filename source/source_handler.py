from enum import Enum
import os
import re

class SourceFileExtension(Enum):
    JAVA = 0
    KOTLIN = 1

class SourceHandler:

    sourceFiles = None
    sourceFileExtensions = {
        SourceFileExtension.JAVA: ".java",
        SourceFileExtension.KOTLIN: ".kt"
    }

    def __init__(self, destinationPath):
        self.destinationPath = destinationPath
        self.findSourceFiles()

    def isJavaSourceFile(self, file):
        return file.endswith(self.sourceFileExtensions[SourceFileExtension.JAVA])
    
    def isKotlinSourceFile(self, file):
        return file.endswith(self.sourceFileExtensions[SourceFileExtension.KOTLIN])

    def writeSourceFile(self, file, content):
        with open(file, "w") as f:
            f.write(content)

    def readSourceFile(self, file):
        with open(file, "r") as f:
            return f.read()

    def matchSourceFiles(self, patterns):
        matches = []
        if self.sourceFiles != None:
            for file in self.sourceFiles:
                with open(file, "r") as f:
                    source = f.read()
                    for pattern in patterns:
                        if re.search(pattern, source):
                            matches.append({"file": file, "pattern": pattern})
        return matches

    def findSourceFiles(self):
        # Check if source files have already been found
        if self.sourceFiles == None:
            self.sourceFiles = []
            # Look for source files in the destination path and
            # add them to the sourceFiles list
            for root, _, files in os.walk(self.destinationPath):
                for file in files:
                    for extension in self.sourceFileExtensions.values():
                        if file.endswith(extension):
                            self.sourceFiles.append(os.path.join(root, file))
                            break
        return self.sourceFiles
