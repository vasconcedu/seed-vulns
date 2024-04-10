from enum import Enum
import os
from lxml import etree as ET

class ExportedConfig(Enum):
    EXPORTED_EXPORTED_IS_TRUE = 1
    EXPORTED_INTENT_FILTER_PRESENT_AND_EXPORTED_NOT_PRESENT = 2
    NOT_EXPORTED_EXPORTED_IS_FALSE = 3
    NOT_EXPORTED_INTENT_FILTER_NOT_PRESENT_AND_EXPORTED_NOT_PRESENT = 4

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
        
    def getManifestString(self):
        return ET.tostring(self.manifestXml, pretty_print=True).decode("utf-8")
        
    def replaceComponentAttrib(self, newComponent, componentName):
        query = ".//" + newComponent.tag + "[@android:name='" + componentName + "']"
        oldComponent = self.manifestXml.find(query, namespaces=self.namespace)
        for attrib in newComponent.attrib:
            oldComponent.attrib[attrib] = newComponent.attrib[attrib]
        
    def findComponentsWithoutExported(self, type):
        query = ".//" + type
        all = []
        for component in self.manifestXml.findall(query, namespaces=self.namespace):
            all.append(component)
        exportedNotPresent = []
        for component in all:
            if not component.attrib.get("{" + list(self.namespace.values())[0] + "}exported"):
                exportedNotPresent.append(component)
        return exportedNotPresent

    def findAllComponents(self, type, exported=None):
        components = []
        if exported == True:

            # In order to find exported components, the query is the following: 
            # 1. exported='true' OR (2. intent-filter AND 3. exported not present)

            # 1. exported='true'
            query = ".//" + type + "[@android:exported='true']"
            for component in self.manifestXml.findall(query, namespaces=self.namespace):
                components.append({
                        "component": component, 
                        "name": component.attrib.get("{" + list(self.namespace.values())[0] + "}name"), 
                        "reason": ExportedConfig.EXPORTED_EXPORTED_IS_TRUE
                    })

            # 3. exported not present
            exportedNotPresent = self.findComponentsWithoutExported(type)

            # 2. those with intent-filter among the exported not present ones
            for component in exportedNotPresent:
                if component.find("intent-filter") is not None:
                    components.append({
                            "component": component, 
                            "name": component.attrib.get("{" + list(self.namespace.values())[0] + "}name"),
                            "reason": ExportedConfig.EXPORTED_INTENT_FILTER_PRESENT_AND_EXPORTED_NOT_PRESENT
                        })
            
        elif exported == False:
            
            # In order to find non-exported components, the query is the following: 
            # 1. exported='false' OR (2. intent-filter not present AND 3. exported not present)

            # 1. exported='false'
            query = ".//" + type + "[@android:exported='false']"
            for component in self.manifestXml.findall(query, namespaces=self.namespace):
                components.append({
                        "component": component, 
                        "name": component.attrib.get("{" + list(self.namespace.values())[0] + "}name"),
                        "reason": ExportedConfig.NOT_EXPORTED_EXPORTED_IS_FALSE
                    })

            # 3. exported not present
            exportedNotPresent = self.findComponentsWithoutExported(type)

            # 2. those without intent-filter among the exported not present ones
            for component in exportedNotPresent:
                if component.find("intent-filter") is None:
                    components.append({
                            "component": component, 
                            "name": component.attrib.get("{" + list(self.namespace.values())[0] + "}name"),
                            "reason": ExportedConfig.NOT_EXPORTED_INTENT_FILTER_NOT_PRESENT_AND_EXPORTED_NOT_PRESENT
                        })

        else:
            query = ".//" + type
            for component in self.manifestXml.findall(query, namespaces=self.namespace):
                components.append({
                    "component": component,
                    "name": component.attrib.get("{" + list(self.namespace.values())[0] + "}name"),
                    "reason": None
                })

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
