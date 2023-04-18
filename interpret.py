import sys
import xml.etree.ElementTree as elemTree
import classes.ArgumentParser as ap
import classes.Parser as xmlpar
import classes.ErrorHandler as err
import classes.Interpret as interpret 

# Arguments
par = ap.ArgumentParser(add_help=False)
argv = par.checkArguments()

# Interpret
parser = xmlpar.Parser(argv.source)
listOfNumbers, listofInstructions = parser.check()
app = interpret.Interpret()
app.isInstructionCorrect(listOfNumbers, listofInstructions) 			
errCode = app.interpret(argv.input, par.isFile)	

# Exit with error, if there is 
if errCode != 0:
	sys.exit(errCode)