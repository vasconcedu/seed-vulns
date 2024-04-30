from enum import Enum
import os
import re

# For now, only XML resource files are supported.
class ResourceFileExtension(Enum):
    XML = 0

# TODO improve this to actually parse XML resource files.
# Since the first version of this tool contains only a single 
# operator that mutates resource files, this class takes the
# dumb approach of just matching patterns in the resource 
# files instead of actually parsing them.
class ResourcesHandler:

    resourceFiles = None

    resourceFileExtensions = {
        ResourceFileExtension.XML: ".xml"
    }

    def __init__(self, destinationPath):
        self.destinationPath = destinationPath

    def writeResourceFile(self, file, content):
        with open(file, "w") as f:
            f.write(content)

    def readResourceFile(self, file):
        with open(file, "r") as f:
            return f.read()

    def matchResourceFiles(self, patterns):
        matches = []
        if self.resourceFiles != None:
            for file in self.resourceFiles:
                with open(file, "r") as f:
                    source = f.read()
                    for pattern in patterns:
                        if re.search(pattern, source):
                            matches.append({"file": file, "pattern": pattern})
        return matches

    def findResourceFiles(self):
        # Check if resource files have already been found
        if self.resourceFiles == None:
            self.resourceFiles = []
            # Look for resource files in the destination path and
            # add them to the resourceFiles list
            for root, _, files in os.walk(self.destinationPath):
                for file in files:
                    for extension in self.resourceFileExtensions.values():
                        # Need to filter out the manifest file here 
                        if file.endswith(extension) and not file.startswith("AndroidManifest"):
                            self.resourceFiles.append(os.path.join(root, file))
                            break
        return self.resourceFiles
