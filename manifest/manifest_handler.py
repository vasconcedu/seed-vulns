import os
from lxml import etree as ET

class ManifestHandler:

    namespace = None 
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
            self.namespace = self.manifestXml.getroot().nsmap
            return True
        except ET.ParseError as e:
            return False

    def findAllComponents(self, type, exported=None):
        components = []
        if exported == True:

            # In order to find exported components, the query is the following: 
            # 1. exported='true' or (2. intent-filter and 3. exported not present)

            # 1. exported='true'
            query = ".//" + type + "[@android:exported='true']"
            for component in self.manifestXml.findall(query, namespaces=self.namespace):
                components.append(component)

            # 3. exported not present
            query = ".//" + type
            all = []
            for component in self.manifestXml.findall(query, namespaces=self.namespace):
                all.append(component)
            exportedNotPresent = []
            for component in all:
                if not component.attrib.get("{" + list(self.namespace.values())[0] + "}exported"):
                    exportedNotPresent.append(component)

            # 2. those with intent-filter among the exported not present ones
            for component in exportedNotPresent:
                if component.find("intent-filter") is not None:
                    components.append(component)
            
        elif exported == False:
            pass
            # TODO continue here
        else:
            for component in self.manifestXml.findall(query, namespaces=self.namespace):
                components.append(component)
        return components

    def findAllActivities(self, exported=None):
        return self.findAllComponents("activity", exported)

    def findAllServices(self, exported=None):
        return self.findAllComponents("service", exported)
    
    def findAllReceivers(self, exported=None):
        return self.findAllComponents("receiver", exported)

    def findAllProviders(self, exported=None):
        return self.findAllComponents("provider", exported)

    def findAllApplicationComponents(self, exported=None):
        if exported == None:
            return self.findAllActivities() + self.findAllServices() + self.findAllReceivers() + self.findAllProviders()
        elif exported == True:
            return self.findAllActivities(True) + self.findAllServices(True) + self.findAllReceivers(True) + self.findAllProviders(True)
        elif exported == False:
            return self.findAllActivities(False) + self.findAllServices(False) + self.findAllReceivers(False) + self.findAllProviders(False)
        else:
            raise ValueError("Invalid value for exported: " + str(exported))
