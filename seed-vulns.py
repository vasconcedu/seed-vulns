#!/usr/bin/python3 

import logging
import argparse
from shutil import copytree
from operators.java.implicit_pending_intent import ImplicitPendingIntent
from operators.operators import OperatorTypes
from operators.xml.improper_export import ImproperExport
from operators.xml.debuggable_application import DebuggableApplication

def main():
    log = setupLogging()
    log.info("========== seed-vulns ==========")

    log.info("Parsing arguments...")
    args = parseArguments()
    sourcePath = args.sourcePath
    destinationPath = args.destinationPath
    operators = args.operators.split(',')
    logArguments(log, sourcePath, destinationPath, operators)

    log.info("Copying the source path to the destination path...")
    copyDestination(log, sourcePath, destinationPath)

    log.info("Instantiating operators...")
    operatorsQueue = instantiateOperators(log, operators)

    if (needManifest(operatorsQueue)):
        log.info("Found queued manifest-based operator. Parsing manifest...")
        # TODO continue here

def needManifest(operatorsQueue):
    for operator in operatorsQueue:
        if operator.type == OperatorTypes.XML:
            return True

def instantiateOperators(log, operators):
    queue = []
    for operator in operators:
        log.info("Instantiating operator: %s", operator)
        match operator:
            case "ImproperExport":
                queue.append(ImproperExport())
            case "DebuggableApplication":
                queue.append(DebuggableApplication())
            case "ImplicitPendingIntent":
                queue.append(ImplicitPendingIntent())
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
