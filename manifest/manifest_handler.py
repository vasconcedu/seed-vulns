import os
import xml.etree.ElementTree as ET

class ManifestHandler:
    manifestPath = None
    manifestXml = None

    def __init__(self, destinationPath):
        self.destinationPath = destinationPath

    def findManifest(self):
        for root, _, files in os.walk(self.destinationPath):
            if "AndroidManifest.xml" in files:
                self.manifestPath = os.path.join(root, "AndroidManifest.xml")
                return True
        return False
    
    def parseManifest(self):
        try:
            self.manifestXml = ET.parse(self.manifestPath)
            return True
        except ET.ParseError as e:
            return False
