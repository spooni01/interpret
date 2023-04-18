import argparse as ap
import sys
import os
import classes.ErrorHandler as err

# Updated ArgumentParser class
class ArgumentParser(ap.ArgumentParser):
    isFile = True # Is false if there is set --source or --input file, if not, is true (= input is in stdin)
    
    # Rewrite error function
    def error(self, message):
        err.ErrorHandler("Wrong arguments, write '--help' for help", 10)
        
    # Add arguments to class    
    def addArguments(self):
        self.add_argument("--help", action="store_true")
        self.add_argument("--source", metavar="FILE", type=str, help="input file with an XML representation of the source code")
        self.add_argument("--input",  metavar="FILE", type=str, help="file with inputs for the actual interpretation of the specified source code")
        return self.parse_args()
    
    # Function will write help
    def writeHelpMessage(self):
        if len(sys.argv) != 2:
            err.ErrorHandler("The '--help' argument must be used separately", 10)
        else:
            self.print_help()
            sys.exit(0)

    # Check if files are set by user and if they are opened corectly
    def openingFileChecker(self, argv):
        if not argv.input and not argv.source:
            err.ErrorHandler("Use at least one argument '--source' or '--input'", 10)
        elif(argv.input and not os.path.isfile(argv.input)) or (argv.source and not os.path.isfile(argv.source)):
            err.ErrorHandler("Problem with opening file", 11)

    # Function will do all the necessary stuff with arguments
    def checkArguments(self):
        argv = self.addArguments()
        if argv.help:
            self.writeHelpMessage()

        self.openingFileChecker(argv)
        
        if not argv.input:
            self.isFile = False
            argv.input = sys.stdin
        if not argv.source:
            argv.source = sys.stdin

        return argv
