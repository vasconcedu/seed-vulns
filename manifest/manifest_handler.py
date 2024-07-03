from enum import Enum
import os
from shutil import copytree, rmtree
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
        self.findManifest()
        self.parseManifest()

    def removeDestinationPath(self):
        rmtree(self.destinationPath, ignore_errors=True)

    def writeManifest(self, to_new_copy=False, copy_index=None):
        # If to_new_copy is True, create a backup of the destination path
        destinationPathBackup = None
        if to_new_copy: 
            destinationPathBackup = "{}_backup".format(self.destinationPath)
            copytree(self.destinationPath, destinationPathBackup)
            
        # Write content to manifest file
        with open(self.manifestPath, "w") as f:
            f.write(self.getManifestString())

        # If to_new_copy is True, move the destination path to a new directory
        # named after the copy index, restore the backup to the original destination
        if to_new_copy:
            newDestinationPath = "{}_{}".format(self.destinationPath, copy_index)
            rmtree(newDestinationPath, ignore_errors=True)
            os.rename(self.destinationPath, newDestinationPath)
            os.rename(destinationPathBackup, self.destinationPath)
            # Need to parse manifest again here 
            self.parseManifest()

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
    
    def queryAndReplaceAttrib(self, query, new, comment):
        old = self.manifestXml.find(query, namespaces=self.namespace)
        old.append(ET.Comment(comment))
        for attrib in new.attrib:
            old.attrib[attrib] = new.attrib[attrib]

    def replaceApplicationAttrib(self, newApplication, comment):
        query = ".//application"
        self.queryAndReplaceAttrib(query, newApplication, comment)

    def replaceComponentAttrib(self, newComponent, componentName, comment):
        query = ".//" + newComponent.tag + "[@android:name='" + componentName + "']"
        self.queryAndReplaceAttrib(query, newComponent, comment)
        
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
        
    def findApplication(self):
        query = ".//application"
        return self.manifestXml.findall(query, namespaces=self.namespace)
