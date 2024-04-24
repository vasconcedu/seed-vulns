#!/usr/bin/python3 

import logging
import argparse
from shutil import copytree
from manifest.manifest_handler import ManifestHandler
from operators.java.hardcoded_secret import HardcodedSecret
from operators.java.implicit_pending_intent import ImplicitPendingIntent
from operators.java.tapjacking_partial_occlusion import TapjackingPartialOcclusion
from operators.operators import OperatorNames, OperatorTypes
from operators.xml.improper_export import ImproperExport
from operators.xml.debuggable_application import DebuggableApplication
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
    logArguments(log, sourcePath, destinationPath, operators)

    # Copy the source path to the destination path. Mutations
    # ovewrite the files in the destination path
    log.info("Copying the source path to the destination path...")
    copyDestination(log, sourcePath, destinationPath)

    # Instantiate operators, by mapping the operator names to
    # the corresponding classes 
    log.info("Instantiating operators...")
    operatorsQueue = instantiateOperators(log, operators)

    # Find and parse Android manifest if needed. That is, if
    # there are any XML-based operators in the queue
    if needManifest(operatorsQueue):
        log.info("Found queued manifest-based operator. Parsing manifest...")
        manifestHandler = ManifestHandler(destinationPath)

        if manifestHandler.findManifest():
            log.info("Manifest found at: %s. Parsing...", manifestHandler.manifestPath)

            if manifestHandler.parseManifest():
                log.info("Manifest parsed successfully")
            else:
                log.error("An error occurred while parsing the manifest. Exiting...")
                exit(1)
        else:
            log.error("Manifest not found, but manifest-based operators specified. Exiting...")
            exit(1)

    # Find source files if needed. That is, if there are any
    # Java-based operators in the queue
    if needSources(operatorsQueue):
        log.info("Found queued source-based operator. Finding source files...")
        sourceHandler = SourceHandler(destinationPath)
        sourceHandler.findSourceFiles()
    
    # Enter mutation loop. For each operator in the queue,
    # apply the mutation to the app and save the mutated app
    # to the destination path
    log.info("Entering mutation loop...")

    # Variable report is a string containing the results of
    # all mutations. It is printed to the console at the end
    report = "\n========== Mutation Report ==========\n"
    for operator in operatorsQueue:
        log.info("Applying operator: %s", operator.name.value)
        if operator.type == OperatorTypes.XML:
            report += operator.mutate(manifestHandler)
        else:
            report += operator.mutate(sourceHandler)
    
    log.info(report)

def needSources(operatorsQueue):
    for operator in operatorsQueue:
        if operator.type == OperatorTypes.JAVA:
            return True

def needManifest(operatorsQueue):
    for operator in operatorsQueue:
        if operator.type == OperatorTypes.XML:
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
            case OperatorNames.TAPJACKING_PARTIAL_OCCLUSION.value:
                queue.append(TapjackingPartialOcclusion(log))
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

def logArguments(log, sourcePath, destinationPath, operators):
    log.info("seed-vulns has been initiated with the following arguments:")
    log.info("- Source path: %s", sourcePath)
    log.info("- Destination path: %s", destinationPath)
    log.info("- Operators: %s", operators)

if __name__ == '__main__':
    main()
