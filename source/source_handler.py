from enum import Enum
import os
import re
from shutil import copytree, rmtree 

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

    def removeDestinationPath(self):
        rmtree(self.destinationPath, ignore_errors=True)

    def writeSourceFile(self, file, content, to_new_copy=False, copy_index=None):
        # If to_new_copy is True, create a backup of the destination path
        destinationPathBackup = None
        if to_new_copy: 
            destinationPathBackup = "{}_backup".format(self.destinationPath)
            copytree(self.destinationPath, destinationPathBackup)

        # Write content to file
        with open(file, "w") as f:
                f.write(content)

        # If to_new_copy is True, move the destination path to a new directory
        # named after the copy index, restore the backup to the original destination
        if to_new_copy:
            newDestinationPath = "{}_{}".format(self.destinationPath, copy_index)
            rmtree(newDestinationPath, ignore_errors=True)
            os.rename(self.destinationPath, newDestinationPath)
            os.rename(destinationPathBackup, self.destinationPath)

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
