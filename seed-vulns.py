#!/usr/bin/python3 

import logging
import argparse
from shutil import copytree
from manifest.manifest_handler import ManifestHandler
from operators.java.hardcoded_secret import HardcodedSecret
from operators.java.implicit_pending_intent import ImplicitPendingIntent
from operators.java.tapjacking_full_occlusion import TapjackingFullOcclusion as TapjackingFullOcclusion_Java
from operators.java.tapjacking_partial_occlusion import TapjackingPartialOcclusion
from operators.java.tapjacking_set_hide_overlay_windows import TapjackingSetHideOverlayWindows
from operators.operators import OperatorNames, OperatorTypes
from operators.xml.improper_export import ImproperExport
from operators.xml.debuggable_application import DebuggableApplication
from operators.xml.plaintext_http import PlaintextHttp
from operators.xml.tapjacking_full_occlusion import TapjackingFullOcclusion as TapjackingFullOcclusion_XML
from resources.resources_handler import ResourcesHandler
from source.source_handler import SourceHandler

def main():
    # Setup logging and print banner to console 
    log = setupLogging()
    log.info("========== seed-vulns ==========")

    # Parse arguments and log them. Need sourcePath, 
    # destinationPath, and operators
    log.info("Parsing arguments...")
    args = parseArguments()
    sourcePath = args.sourcePath
    destinationPath = args.destinationPath
    operators = args.operators.split(',')
    single = args.single
    logArguments(log, sourcePath, destinationPath, operators, single)

    # Copy the source path to the destination path. Mutations
    # shall ovewrite the files in the destination path
    if single:
        log.info("Copying the source path to the destination path...")
        copyDestination(log, sourcePath, destinationPath)

    # Instantiate operators, by mapping the operator names to
    # the corresponding classes 
    log.info("Instantiating operators...")
    operatorsQueue = instantiateOperators(log, operators)

    # Source file handlers 
    manifestHandler = None 
    sourceHandler = None
    resourcesHandler = None

    # If single, then instantiate all source file handlers
    # in advance, since the destination path is always the same
    if single: 
        # Find and parse Android manifest if needed. That is, if
        # there are any XML-based operators in the queue
        if needManifest(operatorsQueue):
            log.info("Found queued manifest-based operators. Parsing manifest...")
            manifestHandler = ManifestHandler(destinationPath)
            log.info("Manifest path: %s", manifestHandler.manifestPath)

        # Find source files if needed. That is, if there are any
        # Java-based operators in the queue
        if needSources(operatorsQueue):
            log.info("Found queued source-based operators. Finding source files...")
            sourceHandler = SourceHandler(destinationPath)
            for sourceFile in sourceHandler.sourceFiles:
                log.info("Source file: %s", sourceFile)

        # Find resource files if needed. That is, if there are any
        # XML-based operators in the queue
        if needResources(operatorsQueue):
            log.info("Found queued resource-based operators. Finding resource files...")
            resourcesHandler = ResourcesHandler(destinationPath)
            for resourceFile in resourcesHandler.resourceFiles:
                log.info("Resource file: %s", resourceFile)
    
    # Enter mutation loop. For each operator in the queue,
    # apply the mutation to the app and save the mutated app
    # to the destination path
    log.info("Entering mutation loop...")

    # Variable report is a string containing the results of
    # all mutations. It is printed to the console at the end
    report = "\n========== Mutation Report ==========\n"
    for operator in operatorsQueue:
        log.info("Applying operator: %s", operator.name.value)
        path = None 
        if not single: 
            path = "{}_{}".format(destinationPath, operator.name.value)
        if operator.type == OperatorTypes.XML_MANIFEST:
            if not single:
                copyDestination(log, sourcePath, path)
                manifestHandler = ManifestHandler(path)
            report += operator.mutate(manifestHandler)
        elif operator.type == OperatorTypes.JAVA:
            if not single: 
                copyDestination(log, sourcePath, path)
                sourceHandler = SourceHandler(path)
                sourceHandler.findSourceFiles()
            report += operator.mutate(sourceHandler)
        elif operator.type == OperatorTypes.XML_RESOURCES:
            if not single: 
                copyDestination(log, sourcePath, path)
                resourcesHandler = ResourcesHandler(path)
                resourcesHandler.findResourceFiles()
            report += operator.mutate(resourcesHandler)
        else: 
            log.error("Invalid operator type: %s", operator.type)
            exit(1)
    
    log.info(report)

def needResources(operatorsQueue):
    for operator in operatorsQueue:
        if operator.type == OperatorTypes.XML_RESOURCES:
            return True

def needSources(operatorsQueue):
    for operator in operatorsQueue:
        if operator.type == OperatorTypes.JAVA:
            return True

def needManifest(operatorsQueue):
    for operator in operatorsQueue:
        if operator.type == OperatorTypes.XML_MANIFEST:
            return True

def instantiateOperators(log, operators):
    queue = []
    for operator in operators:
        log.info("Instantiating operator: %s", operator)

        match operator:
            case OperatorNames.IMPROPER_EXPORT.value:
                queue.append(ImproperExport(log))
            case OperatorNames.DEBUGGABLE_APPLICATION.value:
                queue.append(DebuggableApplication(log))
            case OperatorNames.IMPLICIT_PENDING_INTENT.value:
                queue.append(ImplicitPendingIntent(log))
            case OperatorNames.HARDCODED_SECRET.value:
                queue.append(HardcodedSecret(log))
            # Specifying operator TapjackingFullOcclusion activates 
            # both Java and XML full occlusion operators
            case OperatorNames.TAPJACKING_FULL_OCCLUSION.value:
                queue.append(TapjackingFullOcclusion_XML(log))
                queue.append(TapjackingFullOcclusion_Java(log))
            case OperatorNames.TAPJACKING_PARTIAL_OCCLUSION.value:
                queue.append(TapjackingPartialOcclusion(log))
            case OperatorNames.TAPJACKING_SET_HIDE_OVERLAY_WINDOWS.value:
                queue.append(TapjackingSetHideOverlayWindows(log))
            case OperatorNames.PLAINTEXT_HTTP.value:
                queue.append(PlaintextHttp(log))
            case _:
                log.error("Invalid operator: %s", operator)
                exit(1)

        log.info("Instance of %s has been queued", operator)

    return queue

def copyDestination(log, sourcePath, destinationPath):
    try:
        copytree(sourcePath, destinationPath)
    except Exception as e:
        log.error("An error occurred while copying the source path to the destination path: %s", e)
        exit(1)

def parseArguments():
    parser = argparse.ArgumentParser(description="seed-vulns")

    parser.add_argument('sourcePath', help='Source path containing the original app')
    parser.add_argument('destinationPath', help='Destination path to which the resulting mutated app will be saved')
    parser.add_argument('--operators', help='Comma-separeted list of mutation operators to be applied to the app', required=True)
    parser.add_argument('-s', '--single', help='Output one single higher order mutant containing all mutations', action='store_true')

    args = parser.parse_args()

    return args

def setupLogging():
    log = logging.getLogger('seed-vulns')
    log.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(name)s] %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    return log

def logArguments(log, sourcePath, destinationPath, operators, single):
    log.info("seed-vulns has been initiated with the following arguments:")
    log.info("- Source path: %s", sourcePath)
    log.info("- Destination path: %s", destinationPath)
    log.info("- Operators: %s", operators)
    log.info("- Single: %s", "True" if single else "False")

if __name__ == '__main__':
    main()
